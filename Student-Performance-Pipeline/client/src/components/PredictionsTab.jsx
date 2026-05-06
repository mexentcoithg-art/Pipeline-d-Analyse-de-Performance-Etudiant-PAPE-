import React, { useState, useEffect } from 'react';
import { BrainCircuit, Play, AlertTriangle, ShieldCheck, Download, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function PredictionsTab({ user }) {
    const { t } = useTranslation();
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [training, setTraining] = useState(false);
    const [results, setResults] = useState(null);

    const fetchPredictions = () => {
        setLoading(true);
        let url = '/api/predictions';
        if (user?.role === 'Enseignant' && user?.class_assigned) {
            url += `?class_name=${encodeURIComponent(user.class_assigned)}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                setPredictions(Array.isArray(data) ? data : (data.predictions || []));
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchPredictions();
    }, []);

    const handleTrain = async () => {
        if (user?.role !== 'Admin') return;
        setTraining(true);
        try {
            const res = await fetch('/api/train', { method: 'POST' });
            const data = await res.json();
            setResults(data.results);
            // Automatically regenerate predictions after training
            await fetch('/api/predict_all', { method: 'POST' });
            fetchPredictions();
        } catch (e) {
            console.error(e);
        }
        setTraining(false);
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Header Actions */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div>
                    <h2 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-fuchsia-600 tracking-tight flex items-center gap-3">
                        <BrainCircuit className="text-violet-600" size={28} />
                        {t('predictions.header.title')}
                    </h2>
                    <p className="text-slate-500 mt-1 max-w-xl">
                        {t('predictions.header.subtitle')}
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={fetchPredictions}
                        className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition flex items-center gap-2 text-sm"
                    >
                        {t('predictions.actions.refresh')}
                    </button>
                    {user?.role === 'Admin' && (
                        <button
                            onClick={handleTrain}
                            disabled={training}
                            className="px-5 py-2.5 bg-gradient-to-r from-fuchsia-600 to-violet-600 hover:from-fuchsia-500 hover:to-violet-500 text-white font-bold rounded-xl transition-all duration-300 shadow-lg shadow-fuchsia-600/30 hover:shadow-xl hover:-translate-y-0.5 flex items-center gap-2 text-sm disabled:opacity-70 disabled:hover:translate-y-0"
                        >
                            {training ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
                            {training ? t('predictions.actions.training') : t('predictions.actions.train')}
                        </button>
                    )}
                </div>
            </div>

            {/* Training Results Banner */}
            {results && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex gap-6 items-center flex-wrap animate-in slide-in-from-top-4">
                    <div className="bg-emerald-100 p-2 rounded-lg"><ShieldCheck className="text-emerald-600" /></div>
                    <div>
                        <p className="text-sm text-emerald-800 font-semibold">{t('predictions.banner.success')}</p>
                        <p className="text-xs text-emerald-600 font-medium mt-1">
                            {t('predictions.banner.details', {
                                rf: (results.RandomForest_Accuracy * 100).toFixed(1),
                                auc: (results.RandomForest_AUC * 100).toFixed(1),
                                records: results.records,
                                features: results.features
                            })}
                        </p>
                    </div>
                </div>
            )}

            {/* Predictions Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <h3 className="text-lg font-semibold text-slate-800 tracking-tight">{t('predictions.table.title')}</h3>
                    <span className="bg-violet-100 text-violet-700 text-xs font-bold px-2 py-1 rounded-md">
                        {predictions.length} Records
                    </span>
                </div>

                <div className="overflow-x-auto max-h-[600px] overflow-y-auto custom-scrollbar">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-white text-slate-500 font-semibold sticky top-0 border-b border-slate-100 shadow-sm z-10">
                            <tr>
                                <th className="p-4 px-6">{t('predictions.table.cols.date')}</th>
                                <th className="p-4">{t('predictions.table.cols.massar')}</th>
                                <th className="p-4">{t('predictions.table.cols.gender')}</th>
                                <th className="p-4 text-center">{t('predictions.table.cols.predicted')}</th>
                                <th className="p-4">{t('predictions.table.cols.riskLevel')}</th>
                                <th className="p-4">{t('predictions.table.cols.topFactor')}</th>
                                <th className="p-4">{t('predictions.table.cols.recommendation')}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100/60">
                            {loading ? (
                                <tr><td colSpan="7" className="p-12 text-center text-slate-400 animate-pulse">{t('predictions.table.loading')}</td></tr>
                            ) : predictions.length === 0 ? (
                                <tr><td colSpan="7" className="p-12 text-center text-slate-400">{t('predictions.table.empty')}</td></tr>
                            ) : (
                                predictions.map((p) => {
                                    const prob = (p.probabilite_succes || 0) * 100;
                                    const riskLvl = p.niveau_risque || "";
                                    const isRisk = riskLvl.includes("risque") || prob < 50;
                                    return (
                                        <tr key={p.id_prediction} className="hover:bg-slate-50 transition-colors">
                                            <td className="p-4 px-6 text-slate-500 font-mono text-xs">{p.date_prediction}</td>
                                            <td className="p-4 font-bold text-slate-700">{p.massar_code}</td>
                                            <td className="p-4 text-slate-500">{p.gender}</td>
                                            <td className="p-4 text-center">
                                                <div className="flex flex-col items-center">
                                                    <span className="font-black text-base text-slate-800">{prob.toFixed(1)}%</span>
                                                    <div className="w-16 h-1 mt-1 bg-slate-100 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full transition-all duration-1000 ${prob < 50 ? 'bg-rose-500' : 'bg-emerald-500'}`}
                                                            style={{ width: `${prob}%` }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <span className={`px-3 py-1.5 rounded-md text-xs font-bold flex items-center w-max gap-1.5 shadow-sm ${isRisk ? 'bg-rose-500 text-white shadow-rose-500/30' : 'bg-emerald-500 text-white shadow-emerald-500/30'
                                                    }`}>
                                                    {isRisk ? <AlertTriangle size={14} className="text-white" /> : <ShieldCheck size={14} className="text-white" />}
                                                    {riskLvl || "Inconnu"}
                                                </span>
                                            </td>
                                            <td className="p-4 text-slate-600">
                                                <div className="bg-slate-100 border border-slate-200 px-3 py-1 rounded-lg w-max text-xs font-medium">
                                                    {p.facteur_top}
                                                </div>
                                            </td>
                                            <td className="p-4 text-slate-600 italic text-xs max-w-xs truncate" title={p.recommandation}>
                                                {p.recommandation}
                                            </td>
                                        </tr>
                                    )
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
