import React, { useState, useMemo, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line } from 'recharts';
import { Activity, XOctagon, CheckCircle2, Search, Filter, AlertTriangle, TrendingUp, Users, ChevronUp, ChevronDown, Download, ChevronLeft, ChevronRight, BrainCircuit, FileDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function DashboardTab({ stats, students, loading, pagination, onPageChange, user, onStudentClick, darkMode, aiLoading, featureImportanceProps, classComparisonProps, temporalStatsProps }) {
    const { t } = useTranslation();
    const [searchTerm, setSearchTerm] = useState('');
    const [sortConfig, setSortConfig] = useState({ key: 'id', direction: 'asc' });

    const featureImportance = featureImportanceProps || [];
    const classComparison = classComparisonProps || [];
    const temporalStats = temporalStatsProps || [];

    // Handle Sorting
    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    // Sort Logic
    const sortedStudents = useMemo(() => {
        let sortableStudents = [...students];
        if (sortConfig.key !== null) {
            sortableStudents.sort((a, b) => {
                const aValue = a[sortConfig.key];
                const bValue = b[sortConfig.key];

                if (aValue < bValue) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (aValue > bValue) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableStudents;
    }, [students, sortConfig]);

    // Search Logic (applied locally to the current page/sorted list)
    const filteredStudents = sortedStudents.filter(s => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        return (
            (s.id && s.id.toString().toLowerCase().includes(term)) ||
            (s.school && s.school.toString().toLowerCase().includes(term)) ||
            (s.sex && s.sex.toString().toLowerCase().includes(term)) ||
            (s.massar_code && s.massar_code.toString().toLowerCase().includes(term))
        );
    });

    // CSV Export Logic
    const exportToCSV = () => {
        const headers = ["Massar ID", "Class", "Gender", "Absences", "Participation", "G3"];
        const rows = filteredStudents.map(s => [
            s.id,
            s.school,
            s.sex,
            s.absences,
            s.participation,
            s.G3
        ]);

        let csvContent = "data:text/csv;charset=utf-8,"
            + headers.join(",") + "\n"
            + rows.map(e => e.join(",")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `students_export_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Prepare data for charts
    const riskStatusData = [
        { name: t('dashboard.charts.passing'), value: students.filter(s => parseFloat(s.G3) >= 10).length, color: '#10b981' },
        { name: t('dashboard.charts.atRisk'), value: students.filter(s => parseFloat(s.G3) < 10).length, color: '#ef4444' }
    ];

    const gradeDistribution = students.map(s => ({
        name: `ID ${s.id.slice(-4)}`,
        Final: parseFloat(s.G3)
    })).slice(0, 20);

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Dynamic Header */}
            <header className="flex flex-col md:flex-row justify-between items-end gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h2 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-fuchsia-600 to-indigo-600 tracking-tight dark:from-fuchsia-400 dark:to-indigo-400">
                            {t('dashboard.header.title')}
                        </h2>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider border ${user?.role === 'Admin'
                            ? 'bg-indigo-50 text-indigo-600 border-indigo-100'
                            : user?.role === 'Enseignant'
                                ? 'bg-emerald-50 text-emerald-600 border-emerald-100'
                                : 'bg-amber-50 text-amber-600 border-amber-100'
                            }`}>
                            {user?.role || 'User'}
                        </span>
                        {user?.role === 'Enseignant' && user?.class_assigned && (
                            <span className="px-2 py-0.5 bg-slate-100 text-slate-600 border border-slate-200 rounded text-[10px] font-black uppercase tracking-wider">
                                Classe: {user.class_assigned}
                            </span>
                        )}
                    </div>
                    <p className="text-slate-500 dark:text-slate-400 flex items-center gap-2 font-medium">
                        <Activity size={16} /> {t('dashboard.header.subtitle')}
                    </p>
                </div>
                <div className="flex bg-white dark:bg-slate-900 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-sm items-center gap-2 max-w-sm w-full focus-within:ring-2 focus-within:ring-fuchsia-100 dark:focus-within:ring-fuchsia-900/30 transition-all">
                    <Search size={18} className="text-slate-400 dark:text-slate-500" />
                    <input
                        type="text"
                        placeholder={t('dashboard.header.searchPlaceholder')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="outline-none bg-transparent w-full text-slate-700 dark:text-slate-200 placeholder:text-slate-400 font-medium"
                    />
                </div>
            </header>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KpiCard title={t('dashboard.kpi.averageGrade')} value={`${stats.averageGrade} / 20`} icon={<TrendingUp size={24} />} color="indigo" />
                <KpiCard title={t('dashboard.kpi.passRate')} value={`${stats.passRate}%`} icon={<CheckCircle2 size={24} />} color="emerald" />
                <KpiCard title={t('dashboard.kpi.avgAbsences')} value={stats.absences} icon={<Users size={24} />} color="amber" />
                <KpiCard title={t('dashboard.kpi.atRisk')} value={stats.atRisk} icon={<AlertTriangle size={24} />} color="rose" />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 p-6 flex flex-col hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                            <BrainCircuit size={18} className="text-fuchsia-500" />
                            {t('dashboard.charts.featureImportanceTitle')}
                        </h3>
                    </div>
                    <div className="flex-1 w-full min-h-[300px]">
                        {aiLoading ? (
                            <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest">{t('dashboard.table.loading')}</div>
                        ) : featureImportance.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart layout="vertical" data={featureImportance} margin={{ left: 40, right: 40 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={darkMode ? '#334155' : '#e2e8f0'} />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        dataKey="name"
                                        type="category"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 10, fontWeight: 'bold' }}
                                        width={80}
                                    />
                                    <RechartsTooltip
                                        cursor={{ fill: darkMode ? '#1e293b' : '#f8fafc' }}
                                        contentStyle={{
                                            borderRadius: '16px',
                                            backgroundColor: darkMode ? '#0f172a' : '#ffffff',
                                            border: 'none',
                                            boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
                                            color: darkMode ? '#f1f5f9' : '#1e293b'
                                        }}
                                    />
                                    <Bar dataKey="value" fill="#8b5cf6" radius={[0, 6, 6, 0]} barSize={24} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest opacity-50">Aucune donnée IA disponible</div>
                        )}
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 p-6 flex flex-col hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                            <Users size={18} className="text-indigo-500" />
                            {t('dashboard.charts.classComparisonTitle') || "Performance par Classe"}
                        </h3>
                    </div>
                    <div className="flex-1 w-full h-[300px]">
                        {aiLoading ? (
                            <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest">{t('dashboard.table.loading')}</div>
                        ) : classComparison.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={classComparison}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={darkMode ? '#334155' : '#e2e8f0'} />
                                    <XAxis
                                        dataKey="class_name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 10, fontWeight: 'bold' }}
                                    />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 11 }} domain={[0, 20]} />
                                    <RechartsTooltip
                                        contentStyle={{
                                            borderRadius: '16px',
                                            backgroundColor: darkMode ? '#0f172a' : '#ffffff',
                                            border: 'none',
                                            boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
                                            color: darkMode ? '#f1f5f9' : '#1e293b'
                                        }}
                                    />
                                    <Bar dataKey="avg_grade" name="Moyenne" fill="#6366f1" radius={[6, 6, 0, 0]} barSize={34} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest opacity-50">Aucune donnée par classe</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Temporal Statistics Line Chart */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 p-6 flex flex-col hover:shadow-md transition-shadow">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                        <TrendingUp size={18} className="text-indigo-500" />
                        {t('dashboard.charts.temporalTitle') || "Évolution des Performances"}
                    </h3>
                </div>
                <div className="w-full h-[300px]">
                    {aiLoading ? (
                        <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest">{t('dashboard.table.loading')}</div>
                    ) : temporalStats.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={temporalStats}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={darkMode ? '#334155' : '#e2e8f0'} />
                                <XAxis
                                    dataKey="name"
                                    tick={{ fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 10 }}
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: darkMode ? '#94a3b8' : '#64748b', fontSize: 11 }} domain={[0, 20]} />
                                <RechartsTooltip
                                    contentStyle={{
                                        borderRadius: '16px',
                                        backgroundColor: darkMode ? '#0f172a' : '#ffffff',
                                        border: 'none',
                                        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
                                        color: darkMode ? '#f1f5f9' : '#1e293b'
                                    }}
                                />
                                <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-full text-slate-400 font-bold italic uppercase text-[10px] tracking-widest opacity-50">Aucune tendance disponible</div>
                    )}
                </div>
            </div>

            {/* Table Section */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden group/table">
                <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-50/50 dark:bg-slate-800/20">
                    <div className="flex items-center gap-3">
                        <h3 className="text-lg font-black text-slate-800 dark:text-slate-100 tracking-tight uppercase tracking-wider">{t('dashboard.table.title')}</h3>
                        <span className="bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 text-[10px] uppercase font-black px-2.5 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
                            {t('dashboard.table.results', { count: pagination?.total || 0 })}
                        </span>
                    </div>
                    <button
                        onClick={exportToCSV}
                        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-black uppercase tracking-widest rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-600 transition-all shadow-sm active:scale-95"
                    >
                        <Download size={14} className="text-indigo-500 dark:text-indigo-400" />
                        {t('dashboard.table.export')}
                    </button>
                </div>

                <div className="overflow-x-auto custom-scrollbar">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-white dark:bg-slate-900 text-slate-400 dark:text-slate-500 font-black text-[10px] uppercase tracking-[0.2em] border-b border-slate-100 dark:border-slate-800">
                            <tr>
                                <SortHeader field="id" label={t('dashboard.table.cols.massar')} config={sortConfig} onSort={handleSort} darkMode={darkMode} />
                                <SortHeader field="school" label={t('dashboard.table.cols.class')} config={sortConfig} onSort={handleSort} darkMode={darkMode} />
                                <SortHeader field="sex" label={t('dashboard.table.cols.gender')} config={sortConfig} onSort={handleSort} darkMode={darkMode} />
                                <SortHeader field="absences" label={t('dashboard.table.cols.absences')} config={sortConfig} onSort={handleSort} darkMode={darkMode} />
                                <SortHeader field="participation" label={t('dashboard.table.cols.participation')} config={sortConfig} onSort={handleSort} darkMode={darkMode} />
                                <SortHeader field="G3" label={t('dashboard.table.cols.g3')} config={sortConfig} onSort={handleSort} center darkMode={darkMode} />
                                <th className="p-5 px-6 text-center">{t('dashboard.table.cols.status')}</th>
                                <th className="p-5 px-6 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100/60 dark:divide-slate-800/60 text-slate-700 dark:text-slate-300">
                            {loading ? (
                                <tr><td colSpan="8" className="p-16 text-center text-slate-400 dark:text-slate-500 font-bold italic tracking-widest uppercase text-[10px]"><div className="flex flex-col items-center justify-center gap-4 animate-pulse text-indigo-500 dark:text-indigo-400"><Activity size={32} className="animate-spin" /> {t('dashboard.table.loading')}</div></td></tr>
                            ) : filteredStudents.length === 0 ? (
                                <tr><td colSpan="8" className="p-20 text-center text-slate-400 dark:text-slate-600 font-black uppercase tracking-[0.3em] text-[10px]">{t('dashboard.table.empty')}</td></tr>
                            ) : (
                                filteredStudents.map((student) => (
                                    <TableRow key={student.id} student={student} onClick={() => onStudentClick(student.id)} t={t} darkMode={darkMode} />
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Controls */}
                <div className="p-5 bg-slate-50/80 dark:bg-slate-800/40 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center px-8">
                    <div className="text-[10px] font-black text-slate-400 dark:text-slate-500 tracking-[0.2em] uppercase">
                        {t('dashboard.table.pagination.page', { current: pagination?.page || 1, total: pagination?.total_pages || 1 })}
                    </div>
                    <div className="flex gap-2.5">
                        <button
                            disabled={pagination?.page === 1 || loading}
                            onClick={() => onPageChange(pagination.page - 1)}
                            className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 disabled:opacity-20 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all shadow-sm active:scale-90"
                        >
                            <ChevronLeft size={18} />
                        </button>
                        <button
                            disabled={pagination?.page === pagination?.total_pages || loading}
                            onClick={() => onPageChange(pagination.page + 1)}
                            className="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 disabled:opacity-20 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all shadow-sm active:scale-90"
                        >
                            <ChevronRight size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Subcomponents
function SortHeader({ field, label, config, onSort, center = false, darkMode = false }) {
    const isActive = config.key === field;
    return (
        <th className={`p-5 px-6 cursor-pointer group transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50 ${center ? 'text-center' : ''}`} onClick={() => onSort(field)}>
            <div className={`flex items-center gap-1.5 ${center ? 'justify-center' : ''}`}>
                <span className={`${isActive ? 'text-indigo-600 dark:text-indigo-400 font-black' : 'text-slate-400 dark:text-slate-500'}`}>{label}</span>
                <div className="flex flex-col text-slate-200 dark:text-slate-700 group-hover:text-indigo-300 dark:group-hover:text-indigo-500 transition-colors">
                    <ChevronUp size={10} className={`-mb-0.5 ${isActive && config.direction === 'asc' ? 'text-indigo-600 dark:text-indigo-400' : ''}`} />
                    <ChevronDown size={10} className={`${isActive && config.direction === 'desc' ? 'text-indigo-600 dark:text-indigo-400' : ''}`} />
                </div>
            </div>
        </th>
    );
}

function TableRow({ student, onClick, t, darkMode }) {
    const g3 = parseFloat(student.G3 || 0);
    let status = t('dashboard.table.status.average');
    let statusColor = "bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800";

    if (g3 < 10) {
        status = t('dashboard.table.status.atRisk');
        statusColor = "bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800 shadow-sm shadow-rose-200/50 dark:shadow-none";
    } else if (g3 >= 14) {
        status = t('dashboard.table.status.excellent');
        statusColor = "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800 shadow-sm shadow-emerald-200/50 dark:shadow-none";
    }

    return (
        <tr onClick={onClick} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 hover:shadow-[inset_4px_0_0_0_#4f46e5] dark:hover:shadow-[inset_4px_0_0_0_#818cf8] cursor-pointer transition-all group">
            <td className="p-5 px-6 font-mono text-[10px] text-slate-400 dark:text-slate-600 font-black group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors uppercase tracking-[0.1em]">{student.id}</td>
            <td className="p-5 font-bold text-slate-700 dark:text-slate-200">{student.school}</td>
            <td className="p-5 text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">{student.sex}</td>
            <td className="p-5 px-6">
                <span className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-[10px] font-black border ${parseInt(student.absences) > 5 ? 'bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'}`}>
                    {student.absences}
                </span>
            </td>
            <td className="p-5">
                <div className="flex gap-1">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className={`h-1.5 w-1.5 rounded-full ${i < Math.round(parseFloat(student.participation || 0)) ? "bg-indigo-500 dark:bg-indigo-400 shadow-sm shadow-indigo-300 dark:shadow-indigo-900" : "bg-slate-200 dark:bg-slate-800"}`}></div>
                    ))}
                </div>
            </td>
            <td className="p-5 text-center">
                <div className={`font-black text-lg tabular-nums ${g3 >= 10 ? 'text-slate-800 dark:text-slate-100' : 'text-rose-600 dark:text-rose-400'}`}>{student.G3}</div>
            </td>
            <td className="p-5 text-center">
                <span className={`px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest border ${statusColor}`}>
                    {status}
                </span>
            </td>
            <td className="p-5 text-center" onClick={(e) => e.stopPropagation()}>
                <button
                    onClick={() => window.open(`/api/reports/student/${student.massar_code}`, '_blank')}
                    className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                    title={t('modal.downloadReport')}
                >
                    <FileDown size={18} />
                </button>
            </td>
        </tr>
    );
}

const colorStyles = {
    indigo: { bg: 'bg-gradient-to-br from-fuchsia-600 to-indigo-700', text: 'text-white', textSub: 'text-fuchsia-100', iconBg: 'bg-white/20', border: 'border-transparent shadow-lg shadow-indigo-600/30' },
    emerald: { bg: 'bg-gradient-to-br from-emerald-500 to-teal-600', text: 'text-white', textSub: 'text-emerald-50', iconBg: 'bg-white/20', border: 'border-transparent shadow-lg shadow-teal-500/30' },
    amber: { bg: 'bg-gradient-to-br from-amber-400 to-orange-500', text: 'text-white', textSub: 'text-amber-50', iconBg: 'bg-white/20', border: 'border-transparent shadow-lg shadow-orange-500/30' },
    rose: { bg: 'bg-gradient-to-br from-rose-500 to-pink-600', text: 'text-white', textSub: 'text-pink-100', iconBg: 'bg-white/20', border: 'border-transparent shadow-lg shadow-pink-600/30' },
};

function KpiCard({ title, value, icon, color }) {
    const style = colorStyles[color];
    return (
        <div className={`p-6 rounded-2xl border ${style.border} ${style.bg} relative overflow-hidden group transition-all duration-300 hover:-translate-y-1 hover:shadow-xl`}>
            <div className="absolute -bottom-6 -right-6 w-24 h-24 rounded-full opacity-10 blur-xl bg-white scale-150 transition-transform duration-500 group-hover:scale-110" />
            <div className="relative z-10 flex justify-between items-start">
                <div>
                    <h3 className={`text-[10px] font-black uppercase tracking-[0.2em] ${style.textSub} mb-1.5 opacity-80`}>{title}</h3>
                    <p className={`text-4xl font-black ${style.text} tracking-tight`}>{value}</p>
                </div>
                <div className={`p-3.5 rounded-xl ${style.iconBg} backdrop-blur-md ${style.text} shadow-inner`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}
