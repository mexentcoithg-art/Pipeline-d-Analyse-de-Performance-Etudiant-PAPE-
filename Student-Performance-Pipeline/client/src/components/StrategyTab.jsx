import React, { useState, useEffect } from 'react';
import { Target, AlertTriangle, Users, ChevronDown, ChevronUp, Activity, ShieldCheck, TrendingDown, Info } from 'lucide-react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    Line,
    ComposedChart
} from 'recharts';

export default function StrategyTab({ darkMode }) {
    const [absenteeismData, setAbsenteeismData] = useState(null);
    const [clusterData, setClusterData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedCluster, setSelectedCluster] = useState(null);
    const [clusterStudents, setClusterStudents] = useState([]);
    const [loadingStudents, setLoadingStudents] = useState(false);
    const [selectedTrack, setSelectedTrack] = useState(null);
    const [trackStudents, setTrackStudents] = useState([]);
    const [loadingTrack, setLoadingTrack] = useState(false);

    // Dynamic Analysis States
    const [xFeature, setXFeature] = useState('absences_t1');
    const [yFeature, setYFeature] = useState('moyenne_g1');
    const [loadingImpact, setLoadingImpact] = useState(false);

    const features = [
        { id: 'absences_t1', label: 'Absences' },
        { id: 'participation_g1', label: 'Participation' }
    ];

    const targets = [
        { id: 'moyenne_g1', label: 'Note Finale (G3)' }
    ];

    const fetchImpact = async () => {
        setLoadingImpact(true);
        try {
            const res = await fetch(`/api/analytics/absenteeism-impact?x_col=${xFeature}&y_col=${yFeature}`);
            if (res.ok) {
                setAbsenteeismData(await res.json());
            }
        } catch (e) {
            console.error("Impact Fetch Error:", e);
        } finally {
            setLoadingImpact(false);
        }
    };

    const handleClusterClick = async (clusterId) => {
        if (selectedCluster === clusterId) {
            setSelectedCluster(null);
            return;
        }
        setSelectedCluster(clusterId);
        setLoadingStudents(true);
        try {
            const res = await fetch(`/api/analytics/cluster-students/${clusterId}`);
            if (res.ok) {
                const data = await res.json();
                setClusterStudents(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error("Fetch students error:", e);
        } finally {
            setLoadingStudents(false);
        }
    };

    const handleTrackClick = async (trackName) => {
        if (selectedTrack === trackName) {
            setSelectedTrack(null);
            return;
        }
        setSelectedTrack(trackName);
        setLoadingTrack(true);
        try {
            const res = await fetch(`/api/analytics/orientation-students/${encodeURIComponent(trackName)}`);
            if (res.ok) {
                const data = await res.json();
                setTrackStudents(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error("Fetch orientation students error:", e);
        } finally {
            setLoadingTrack(false);
        }
    };

    useEffect(() => {
        const fetchInitialData = async () => {
            setLoading(true);
            try {
                const clusterRes = await fetch(`/api/analytics/student-clusters`);
                if (clusterRes.ok) setClusterData(await clusterRes.json());
                await fetchImpact();
            } catch (e) {
                console.error("Strategy Fetch Error:", e);
            } finally {
                setLoading(false);
            }
        };
        fetchInitialData();
    }, []);

    useEffect(() => {
        if (!loading) fetchImpact();
    }, [xFeature, yFeature]);

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* SECTION 1: DYNAMIC IMPACT ANALYSIS */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-xl shadow-indigo-500/5 overflow-hidden">
                <div className="p-6 border-b border-slate-50 dark:border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 bg-rose-50 text-rose-500 dark:bg-rose-500/10 rounded-lg">
                            <Activity size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-black text-slate-800 dark:text-white uppercase tracking-wider">
                                Analyse d'Impact Dynamique
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-widest mt-0.5">
                                Régression & Corrélation Avancée
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 p-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                        <span className="text-[10px] font-bold text-slate-400 uppercase ml-2 px-1">X:</span>
                        <select
                            value={xFeature}
                            onChange={(e) => setXFeature(e.target.value)}
                            className="bg-transparent text-xs font-bold text-slate-600 dark:text-slate-200 outline-none focus:ring-0 cursor-pointer"
                        >
                            {features.map(f => <option key={f.id} value={f.id} className="dark:bg-slate-900">{f.label}</option>)}
                        </select>
                        <div className="w-px h-4 bg-slate-200 dark:bg-slate-700 mx-1"></div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase ml-1 px-1">Y:</span>
                        <select
                            value={yFeature}
                            onChange={(e) => setYFeature(e.target.value)}
                            className="bg-transparent text-xs font-bold text-slate-600 dark:text-slate-200 outline-none focus:ring-0 cursor-pointer"
                        >
                            {targets.map(t => <option key={t.id} value={t.id} className="dark:bg-slate-900">{t.label}</option>)}
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3">
                    {/* Left Panel: Stats & Interpretation */}
                    <div className="p-8 border-r border-slate-50 dark:border-slate-800 space-y-8 bg-slate-50/30 dark:bg-slate-800/20">
                        {loadingImpact ? (
                            <div className="h-full flex flex-col items-center justify-center space-y-4 py-12">
                                <div className="w-8 h-8 border-4 border-rose-400 border-t-transparent rounded-full animate-spin"></div>
                                <p className="text-sm font-medium text-slate-400">Calcul de l'impact...</p>
                            </div>
                        ) : absenteeismData && !absenteeismData.error ? (
                            <>
                                <div className="text-center">
                                    <div className={`text-5xl font-black mb-2 ${absenteeismData.impact_coefficient < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                        {absenteeismData.impact_coefficient > 0 ? '+' : ''}{absenteeismData.impact_coefficient?.toFixed(2)} pts
                                    </div>
                                    <p className="text-base font-bold text-slate-700 dark:text-slate-200 leading-relaxed px-2">
                                        {absenteeismData.interpretation}
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex flex-col">
                                        <div className="flex justify-between items-end mb-2">
                                            <span className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                                                <ShieldCheck size={14} className="text-indigo-500" />
                                                Fiabilité du Modèle
                                            </span>
                                            <span className="text-sm font-black text-indigo-500">{(absenteeismData.reliability_score * 100).toFixed(0)}%</span>
                                        </div>
                                        <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-indigo-500 to-fuchsia-500 transition-all duration-1000"
                                                style={{ width: `${Math.max(5, absenteeismData.reliability_score * 100)}%` }}
                                            ></div>
                                        </div>
                                        <p className="text-[10px] text-slate-400 mt-2 italic flex items-center gap-1">
                                            <Info size={10} /> Indice R² : mesure de la force statistique du lien observé.
                                        </p>
                                    </div>

                                    {absenteeismData.critical_threshold && (
                                        <div className={`p-4 rounded-2xl border ${absenteeismData.impact_coefficient < 0 ? 'bg-rose-50 dark:bg-rose-500/10 border-rose-100 dark:border-rose-500/20' : 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-100 dark:border-emerald-500/20'}`}>
                                            <div className="flex gap-3">
                                                <AlertTriangle className={absenteeismData.impact_coefficient < 0 ? 'text-rose-500' : 'text-emerald-500'} size={20} />
                                                <div>
                                                    <p className={`text-xs font-black uppercase tracking-tight mb-1 ${absenteeismData.impact_coefficient < 0 ? 'text-rose-700 dark:text-rose-400' : 'text-emerald-700 dark:text-emerald-400'}`}>
                                                        Seuil de Rupture Détecté
                                                    </p>
                                                    <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                                                        L'IA identifie une rupture majeure des résultats à partir de <span className="font-black underline">{absenteeismData.critical_threshold.toFixed(1)}</span> {features.find(f => f.id === xFeature)?.label}.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center p-8 text-center bg-slate-100/50 dark:bg-slate-800/30 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700">
                                <AlertTriangle className="text-slate-400 mb-3" size={32} />
                                <p className="text-slate-500 font-bold uppercase text-[10px] tracking-widest">Données Insuffisantes</p>
                                <p className="text-xs text-slate-400 mt-2">Le modèle nécessite plus de variations dans les données pour établir un lien statistique fiable.</p>
                            </div>
                        )}
                    </div>

                    {/* Right Panel: Chart */}
                    <div className="lg:col-span-2 p-6 min-h-[400px]">
                        {absenteeismData && absenteeismData.plot_data ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart
                                    margin={{ top: 20, right: 30, bottom: 20, left: 10 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={darkMode ? "#334155" : "#f1f5f9"} />
                                    <XAxis
                                        type="number"
                                        dataKey="x"
                                        name={features.find(f => f.id === xFeature)?.label}
                                        stroke={darkMode ? "#94a3b8" : "#64748b"}
                                        fontSize={10}
                                        fontWeight="bold"
                                        label={{ value: features.find(f => f.id === xFeature)?.label, position: 'insideBottom', offset: -10, fill: darkMode ? "#94a3b8" : "#64748b", fontSize: 10, fontWeight: 'bold' }}
                                    />
                                    <YAxis
                                        type="number"
                                        dataKey="y"
                                        name="Note"
                                        stroke={darkMode ? "#94a3b8" : "#64748b"}
                                        fontSize={10}
                                        domain={[0, 20]}
                                        fontWeight="bold"
                                        label={{ value: 'Performance (0-20)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: darkMode ? "#94a3b8" : "#64748b", fontSize: 10, fontWeight: 'bold' } }}
                                    />
                                    <Tooltip
                                        cursor={{ strokeDasharray: '3 3' }}
                                        content={({ active, payload }) => {
                                            if (active && payload && payload.length) {
                                                return (
                                                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-3 rounded-lg shadow-xl ring-1 ring-slate-900/5">
                                                        <p className="text-[10px] font-black uppercase text-slate-400 mb-1">Détail Étudiant</p>
                                                        <p className="text-xs font-bold text-slate-800 dark:text-white">X ({features.find(f => f.id === xFeature)?.label}) : {payload[0].value}</p>
                                                        <p className="text-xs font-bold text-slate-800 dark:text-white">Y (Performance) : {payload[1] ? payload[1].value.toFixed(2) : payload[0].payload.y.toFixed(2)}</p>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Scatter
                                        name="Étudiants"
                                        data={absenteeismData.plot_data.points}
                                        fill="#a855f7"
                                        fillOpacity={0.6}
                                    />
                                    <Line
                                        data={absenteeismData.plot_data.regression_line}
                                        type="monotone"
                                        dataKey="y"
                                        stroke={absenteeismData.impact_coefficient < 0 ? "#f43f5e" : "#10b981"}
                                        strokeWidth={3}
                                        dot={false}
                                        activeDot={false}
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-300 italic text-sm">
                                Graphique non disponible.
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                {/* Student Clustering Card */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-100 dark:border-slate-800 shadow-xl shadow-indigo-500/5">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2.5 bg-indigo-50 text-indigo-500 dark:bg-indigo-500/10 rounded-lg">
                            <Users size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-black text-slate-800 dark:text-white uppercase tracking-wider">
                                Profils d'Élèves
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-widest mt-0.5">
                                Clustering K-Means
                            </p>
                        </div>
                    </div>

                    {clusterData && clusterData.profiles_detected ? (
                        <div className="space-y-3">
                            {Object.entries(clusterData.profiles_detected).map(([key, label], i) => {
                                const clusterId = parseInt(key);
                                const isSelected = selectedCluster === clusterId;
                                return (
                                    <div key={key} className="space-y-2">
                                        <div
                                            onClick={() => handleClusterClick(clusterId)}
                                            className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-colors ${isSelected ? 'bg-indigo-50 dark:bg-indigo-900/30 ring-1 ring-indigo-200 dark:ring-indigo-800' : 'bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-3 h-3 rounded-full ${label.includes('Intermédiaire') ? 'bg-amber-400' :
                                                        label.includes('Moteur') ? 'bg-emerald-500' :
                                                            label.includes('Accompagnement') ? 'bg-rose-500' : 'bg-slate-400'
                                                    }`}></div>
                                                <span className="font-semibold text-slate-700 dark:text-slate-200">
                                                    Cluster {clusterId + 1} : {label}
                                                </span>
                                            </div>
                                            {isSelected ? <ChevronUp size={16} className="text-indigo-500" /> : <ChevronDown size={16} className="text-slate-400" />}
                                        </div>

                                        {isSelected && (
                                            <div className="p-4 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm animate-in fade-in zoom-in-95 duration-200 overflow-x-auto max-h-80 overflow-y-auto">
                                                {loadingStudents ? (
                                                    <div className="text-center text-sm text-slate-500 py-4 font-medium animate-pulse">Chargement des étudiants...</div>
                                                ) : clusterStudents.length === 0 ? (
                                                    <div className="text-center text-sm text-slate-500 py-4">Aucun étudiant trouvé dans ce groupe.</div>
                                                ) : (
                                                    <table className="w-full text-left text-sm whitespace-nowrap">
                                                        <thead>
                                                            <tr className="text-slate-400 dark:text-slate-500 border-b border-slate-100 dark:border-slate-700">
                                                                <th className="pb-2 font-medium">Code Massar</th>
                                                                <th className="pb-2 font-medium">Classe</th>
                                                                <th className="pb-2 font-medium text-center">Moyenne</th>
                                                                <th className="pb-2 font-medium">Matières Faibles</th>
                                                                <th className="pb-2 font-medium">Matières Fortes</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="divide-y divide-slate-50 dark:divide-slate-700/50">
                                                            {clusterStudents.map(student => (
                                                                <tr key={student.id_etudiant} className="text-slate-600 dark:text-slate-300">
                                                                    <td className="py-2.5 font-medium">{student.massar_code}</td>
                                                                    <td className="py-2.5">{student.classe}</td>
                                                                    <td className="py-2.5 text-center font-bold text-slate-800 dark:text-slate-200">
                                                                        {student.moyenne_generale !== null ? student.moyenne_generale.toFixed(2) : '-'}
                                                                    </td>
                                                                    <td className="py-2.5">
                                                                        {student.matieres_faibles && student.matieres_faibles.length > 0 ? (
                                                                            <div className="flex flex-wrap gap-1">
                                                                                {student.matieres_faibles.map(mf => (
                                                                                    <span key={mf.matiere} className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-600 dark:bg-rose-500/10 dark:text-rose-400 border border-rose-100 dark:border-rose-500/20">
                                                                                        {mf.matiere} ({parseFloat(mf.note).toFixed(1)})
                                                                                    </span>
                                                                                ))}
                                                                            </div>
                                                                        ) : (
                                                                            <span className="text-slate-400 dark:text-slate-500 text-xs italic">Aucune</span>
                                                                        )}
                                                                    </td>
                                                                    <td className="py-2.5">
                                                                        {student.matieres_fortes && student.matieres_fortes.length > 0 ? (
                                                                            <div className="flex flex-wrap gap-1">
                                                                                {student.matieres_fortes.map(mf => (
                                                                                    <span key={mf.matiere} className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-500/20">
                                                                                        {mf.matiere} ({parseFloat(mf.note).toFixed(1)})
                                                                                    </span>
                                                                                ))}
                                                                            </div>
                                                                        ) : (
                                                                            <span className="text-slate-400 dark:text-slate-500 text-xs italic">Aucune</span>
                                                                        )}
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <p className="text-slate-400">Modèle de profilage non initialisé.</p>
                    )}
                </div>

                {/* Orientation Recommendation Trends */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-100 dark:border-slate-800 shadow-xl shadow-indigo-500/5">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2.5 bg-emerald-50 text-emerald-500 dark:bg-emerald-500/10 rounded-lg">
                            <Target size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-black text-slate-800 dark:text-white uppercase tracking-wider">
                                Tendances d'Orientation
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-widest mt-0.5">
                                Recommandation IA (Cycle Lycée)
                            </p>
                        </div>
                    </div>

                    {clusterData && clusterData.orientation_distribution ? (
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {['Scientifique', 'Littéraire', 'Formation Professionnelle'].map((track) => {
                                    const count = clusterData.orientation_distribution[track] || 0;
                                    const isActive = selectedTrack === track;
                                    const trackColors = {
                                        'Scientifique': 'bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400',
                                        'Littéraire': 'bg-purple-50 dark:bg-purple-500/10 border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400',
                                        'Formation Professionnelle': 'bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-800 text-amber-600 dark:text-amber-400',
                                    };
                                    const activeRing = isActive ? 'ring-2 ring-indigo-400 dark:ring-indigo-500 shadow-lg' : '';
                                    const colorClass = trackColors[track] || 'bg-slate-50 dark:bg-slate-800/50 border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-300';
                                    return (
                                        <div
                                            key={track}
                                            onClick={() => handleTrackClick(track)}
                                            className={`p- relative overflow-hidden p-4 rounded-xl border cursor-pointer transition-all hover:scale-[1.02] ${colorClass} ${activeRing}`}
                                        >
                                            <div className="flex items-center justify-between">
                                                <p className="text-[10px] font-black uppercase tracking-widest mb-1">{track}</p>
                                                {isActive ? <ChevronUp size={14} /> : <TrendingDown size={14} className="opacity-0" />}
                                            </div>
                                            <p className="text-2xl font-black text-slate-800 dark:text-white">{count}</p>
                                            <p className="text-xs text-slate-500 font-medium mt-1">Élèves concernés</p>
                                        </div>
                                    );
                                })}
                            </div>

                            {selectedTrack && (
                                <div className="p-4 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-100 dark:border-slate-700 shadow-sm animate-in fade-in zoom-in-95 duration-200 overflow-x-auto max-h-96 overflow-y-auto">
                                    {loadingTrack ? (
                                        <div className="text-center text-sm text-slate-500 py-4 font-medium animate-pulse">Chargement des étudiants...</div>
                                    ) : (
                                        <table className="w-full text-left text-sm whitespace-nowrap">
                                            <thead>
                                                <tr className="text-slate-400 dark:text-slate-500 border-b border-slate-100 dark:border-slate-700">
                                                    <th className="pb-2 font-medium">Code</th>
                                                    <th className="pb-2 font-medium">Confiance</th>
                                                    <th className="pb-2 font-medium">Analyse / Décision</th>
                                                    <th className="pb-2 font-medium">Matières Dominantes</th>
                                                    <th className="pb-2 font-medium text-center">Note G.</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-slate-50 dark:divide-slate-700/50">
                                                {trackStudents.map(student => (
                                                    <tr key={student.massar_code} className="text-slate-600 dark:text-slate-300">
                                                        <td className="py-2.5 font-bold">{student.massar_code}</td>
                                                        <td className="py-2.5 text-center px-1">
                                                            <div className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-[10px] font-black text-slate-500">
                                                                {((student.confidence || 0.7) * 100).toFixed(0)}%
                                                            </div>
                                                        </td>
                                                        <td className="py-2.5 max-w-xs whitespace-normal">
                                                            <p className="text-[11px] leading-tight text-slate-500 italic">
                                                                {student.interpretation || "Analyse multicritère basée sur les coefficients."}
                                                            </p>
                                                        </td>
                                                        <td className="py-2.5">
                                                            <div className="flex flex-wrap gap-1">
                                                                {student.matieres_dominantes?.map(m => (
                                                                    <span key={m.matiere} className="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-500 text-[10px] font-black rounded uppercase border border-indigo-100 dark:border-indigo-500/20">
                                                                        {m.matiere} ({m.note.toFixed(1)})
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </td>
                                                        <td className="py-2.5 text-center font-black px-2 text-indigo-500">{student.moyenne_generale?.toFixed(2)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className="text-slate-400">Calcul des tendances en cours...</p>
                    )}
                </div>
            </div>

        </div>
    );
}
