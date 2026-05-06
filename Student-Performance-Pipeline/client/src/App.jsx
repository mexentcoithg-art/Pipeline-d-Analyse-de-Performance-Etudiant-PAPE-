import React, { useState, useEffect } from "react";
import {
  GraduationCap,
  Database,
  ServerCrash,
  LayoutDashboard,
  BrainCircuit,
  BarChart3,
  Globe,
  Upload,
  Moon,
  Sun,
  AlertTriangle,
  CheckCircle2,
  LogIn,
  Target,
} from "lucide-react";
import { useTranslation } from "react-i18next";

import DashboardTab from "./components/DashboardTab";
import PredictionsTab from "./components/PredictionsTab";
import EdaTab from "./components/EdaTab";
import StudentModal from "./components/StudentModal";
import PipelineModal from "./components/PipelineModal";
import Login from "./components/Login";
import AboutTab from "./components/AboutTab";
import StrategyTab from "./components/StrategyTab";
import NotificationsPopover from "./components/NotificationsPopover";

function App() {
  const { t, i18n } = useTranslation();
  const API_BASE_URL = '';
  const [stats, setStats] = useState({
    apiStatus: "loading", // Changed to lowercase for consistency with new logic
    averageGrade: 0,
    passRate: 0,
    absences: 0,
    atRisk: 0,
  });
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(true);
  const [aiStats, setAiStats] = useState({
    featureImportance: [],
    classComparison: [],
    temporalStats: [],
  });

  // Navigation State
  const [activeTab, setActiveTab] = useState("dashboard"); // 'dashboard' | 'predictions' | 'eda'

  // Modal State
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark",
  );
  const [toasts, setToasts] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem("auth") === "true",
  );
  const [user, setUser] = useState(
    JSON.parse(localStorage.getItem("user") || "null")
  );

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  const addToast = (message, type = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const [pagination, setPagination] = useState({
    page: 1,
    total: 0,
    total_pages: 1,
  });

  useEffect(() => {
    if (isAuthenticated) {
      // Fetch Stats
      const statsUrl = user?.role === 'Enseignant' && user?.class_assigned
        ? `${API_BASE_URL}/api/stats?class_name=${encodeURIComponent(user.class_assigned)}`
        : `${API_BASE_URL}/api/stats`;

      fetch(statsUrl)
        .then((res) => {
          if (!res.ok) throw new Error("Stats fetch failed");
          return res.json();
        })
        .then((data) => {
          setStats((prev) => ({ ...prev, ...data, apiStatus: "online" }));
        })
        .catch((err) => {
          console.error("Stats fetch error:", err);
          setStats((prev) => ({ ...prev, apiStatus: "offline" }));
        });

      const fetchAiStats = () => {
        setAiLoading(true);

        const fetchFeat = fetch(`${API_BASE_URL}/api/feature-importance`)
          .then((res) => res.json())
          .then((data) =>
            setAiStats((prev) => ({ ...prev, featureImportance: data })),
          )
          .catch((err) =>
            console.error("Feature Importance fetch failed:", err),
          );

        const fetchComp = fetch(`${API_BASE_URL}/api/class-comparison`)
          .then((res) => res.json())
          .then((data) =>
            setAiStats((prev) => ({ ...prev, classComparison: data })),
          )
          .catch((err) => console.error("Class Comparison fetch failed:", err));

        const fetchTemp = fetch(`${API_BASE_URL}/api/temporal-stats`)
          .then((res) => res.json())
          .then((data) =>
            setAiStats((prev) => ({ ...prev, temporalStats: data })),
          )
          .catch((err) => console.error("Temporal Stats fetch failed:", err));

        Promise.allSettled([fetchFeat, fetchComp, fetchTemp]).finally(() => {
          setAiLoading(false);
        });
      };

      fetchAiStats();
      fetchStudents(1);
    }
  }, [isAuthenticated]);
  function fetchStudents(page = 1) {
    setLoading(true);
    let url = `${API_BASE_URL}/api/students?page=${page}&per_page=50`;

    if (user?.role === 'Enseignant' && user?.class_assigned) {
      url += `&class_name=${encodeURIComponent(user.class_assigned)}`;
    }

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setStudents(data.students || []);
        setPagination({
          page: data.page,
          total: data.total,
          total_pages: data.total_pages,
        });
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
        addToast(t("common.error.api") || "Erreur API", "error");
      });
  };

  const toggleLanguage = () => {
    const newLang = i18n.language.startsWith("fr") ? "en" : "fr";
    i18n.changeLanguage(newLang);
    addToast(newLang === "fr" ? "Langue : Français" : "Language: English");
  };

  const allTabs = [
    {
      id: "dashboard",
      label: t("app.tabs.dashboard"),
      icon: <LayoutDashboard size={18} />,
      roles: ["Admin", "Enseignant", "Direction"]
    },
    {
      id: "predictions",
      label: t("app.tabs.predictions"),
      icon: <BrainCircuit size={18} />,
      roles: ["Admin", "Enseignant"]
    },
    {
      id: "eda",
      label: t("app.tabs.eda"),
      icon: <BarChart3 size={18} />,
      roles: ["Admin"]
    },
    {
      id: "strategy",
      label: "Stratégie",
      icon: <Target size={18} />,
      roles: ["Admin", "Direction"]
    },
    {
      id: "about",
      label: t("app.tabs.about"),
      icon: <Globe size={18} />,
      roles: ["Admin", "Enseignant", "Direction"]
    },
  ];

  const tabs = allTabs.filter(tab => tab.roles.includes(user?.role));

  if (!isAuthenticated) {
    return (
      <Login
        onLogin={(userData) => {
          setIsAuthenticated(true);
          setUser(userData);
          localStorage.setItem("auth", "true");
          localStorage.setItem("user", JSON.stringify(userData));
          addToast(`${t("login.success") || "Bienvenue"}, ${userData.username}`);
        }}
        darkMode={darkMode}
      />
    );
  }

  return (
    <div
      className={`min-h-screen relative overflow-hidden transition-colors duration-300 selection:bg-fuchsia-100 selection:text-fuchsia-900 font-sans ${darkMode ? "bg-slate-950 text-slate-100" : "bg-slate-50 text-slate-900"}`}
    >
      {/* Toast Notifications */}
      <div className="fixed top-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center gap-3 px-6 py-4 rounded-2xl shadow-2xl backdrop-blur-md border animate-in slide-in-from-right-8 fade-in duration-300 ${toast.type === "error"
              ? "bg-rose-500/95 text-white border-rose-400"
              : "dark:bg-slate-800/95 bg-white/95 text-slate-800 dark:text-slate-100 border-slate-200 dark:border-slate-700"
              }`}
          >
            {toast.type === "error" ? (
              <AlertTriangle size={18} />
            ) : (
              <CheckCircle2 size={18} className="text-emerald-500" />
            )}
            <p className="text-sm font-black tracking-tight">{toast.message}</p>
          </div>
        ))}
      </div>
      {/* Animated Background Elements */}
      <div className="absolute top-0 -left-4 w-96 h-96 bg-fuchsia-300 dark:bg-fuchsia-900 rounded-full mix-blend-multiply dark:mix-blend-overlay filter blur-[100px] opacity-20 dark:opacity-30 animate-blob"></div>
      <div className="absolute top-0 -right-4 w-96 h-96 bg-indigo-300 dark:bg-indigo-900 rounded-full mix-blend-multiply dark:mix-blend-overlay filter blur-[100px] opacity-20 dark:opacity-30 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-32 left-1/2 w-96 h-96 bg-violet-300 dark:bg-violet-900 rounded-full mix-blend-multiply dark:mix-blend-overlay filter blur-[100px] opacity-20 dark:opacity-30 animate-blob animation-delay-4000"></div>

      {/* Navigation Bar */}
      <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-fuchsia-600 to-indigo-600 p-2.5 rounded-xl shadow-lg shadow-fuchsia-600/20 text-white">
              <GraduationCap size={24} strokeWidth={2.5} />
            </div>
            <h1 className="text-2xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-600 to-indigo-600">
              {t("app.title")}
            </h1>
          </div>

          {/* Navigation Tabs */}
          <div className="hidden md:flex bg-slate-100/80 dark:bg-slate-800/80 p-1.5 rounded-2xl border border-slate-200 dark:border-slate-700 backdrop-blur-sm transition-colors duration-300">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-bold transition-all duration-300 ${activeTab === tab.id
                  ? "bg-white dark:bg-slate-700 text-fuchsia-600 dark:text-fuchsia-400 shadow-md ring-1 ring-fuchsia-100 dark:ring-fuchsia-900/30 scale-105"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-slate-700/50"
                  }`}
              >
                {tab.icon}
                <span className="hidden md:inline">{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Actions: Upload, Language, API Status */}
          <div className="flex items-center gap-3 space-x-2">
            {user?.role === "Admin" && (
              <button
                onClick={() => setShowUploadModal(true)}
                className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-fuchsia-500 to-indigo-500 hover:from-fuchsia-400 hover:to-indigo-400 text-white font-bold rounded-xl transition-all text-sm shadow-md shadow-fuchsia-500/20 hover:shadow-lg hover:-translate-y-0.5"
                title={t("upload.button")}
              >
                <Upload size={16} />
                <span className="hidden lg:inline">{t("upload.button")}</span>
              </button>
            )}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="flex items-center gap-2 px-3 py-2 bg-slate-100/80 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold rounded-xl border border-slate-200 dark:border-slate-700 transition-all text-sm"
              title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {darkMode ? (
                <Sun size={16} className="text-amber-500" />
              ) : (
                <Moon size={16} className="text-indigo-500" />
              )}
            </button>
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-2 px-3 py-2 bg-slate-100/80 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold rounded-xl border border-slate-200 dark:border-slate-700 transition-all text-sm uppercase"
              title="Changer de langue / Change language"
            >
              <Globe size={16} className="text-indigo-500" />
              {i18n.language.startsWith("fr") ? "FR" : "EN"}
            </button>

            <NotificationsPopover API_BASE_URL={API_BASE_URL} user={user} />

            <button
              onClick={() => {
                setIsAuthenticated(false);
                setUser(null);
                localStorage.removeItem("auth");
                localStorage.removeItem("user");
                addToast("Déconnexion réussie");
              }}
              className="p-2.5 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 rounded-xl border border-slate-200 dark:border-slate-700 hover:text-rose-500 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-all shadow-sm active:scale-90"
              title="Logout"
            >
              <LogIn size={20} className="rotate-180" />
            </button>

            <div
              className={`flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-bold shadow-sm backdrop-blur-sm transition-colors duration-300 ${stats.apiStatus === "online" ? "bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800" : "bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800"}`}
            >
              {stats.apiStatus === "online" ? (
                <>
                  <Database size={16} className="animate-pulse" />{" "}
                  {t("app.apiOnline")}
                </>
              ) : (
                <>
                  <ServerCrash size={16} /> {t("app.apiOffline")}
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto p-6 max-w-7xl relative z-10 pt-8">
        {activeTab === "dashboard" && (
          <DashboardTab
            stats={stats}
            students={students}
            loading={loading}
            pagination={pagination}
            onPageChange={fetchStudents}
            user={user}
            onStudentClick={setSelectedStudentId}
            showToast={addToast}
            darkMode={darkMode}
            aiLoading={aiLoading}
            featureImportanceProps={aiStats.featureImportance}
            classComparisonProps={aiStats.classComparison}
            temporalStatsProps={aiStats.temporalStats}
          />
        )}

        {activeTab === "predictions" && <PredictionsTab user={user} />}

        {activeTab === "eda" && <EdaTab user={user} />}

        {activeTab === "strategy" && <StrategyTab darkMode={darkMode} />}

        {activeTab === "about" && <AboutTab darkMode={darkMode} />}
      </main>

      {/* Modals */}
      <StudentModal
        studentId={selectedStudentId}
        onClose={() => setSelectedStudentId(null)}
      />
      <PipelineModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onPipelineComplete={() => {
          fetchStudents(1);
          // Refresh global stats
          fetch(`${API_BASE_URL}/api/stats`).then(r => r.json()).then(data => setStats(prev => ({ ...prev, ...data }))).catch(console.error);
          addToast("Pipeline terminé avec succès !");
        }}
      />
    </div>
  );
}

export default App;
