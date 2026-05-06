import React, { useState, useRef, useEffect } from 'react';
import { Upload, X, FileSpreadsheet, CheckCircle2, AlertCircle, Loader2, ArrowRight, ArrowLeft, Database, Play, History, Trash2, Calendar, LayoutList, Settings2, Table2, Target, Columns3 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const STEPS = {
    UPLOAD: 'upload',
    CONFIG: 'config',
    PROCESS: 'process',
    HISTORY: 'history'
};

export default function PipelineModal({ isOpen, onClose, onPipelineComplete }) {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState(STEPS.UPLOAD);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [ingesting, setIngesting] = useState(false);
    const [idImport, setIdImport] = useState(null);
    const [tempPath, setTempPath] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [pipelineResult, setPipelineResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [importsHistory, setImportsHistory] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(false);
    const [confirmingDelete, setConfirmingDelete] = useState(null);

    // Config state
    const [mode, setMode] = useState('add');
    const [idColumn, setIdColumn] = useState('');
    const [targetColumn, setTargetColumn] = useState('');

    const inputRef = useRef(null);

    useEffect(() => {
        if (isOpen && activeTab === STEPS.HISTORY) fetchHistory();
    }, [isOpen, activeTab]);

    const fetchHistory = async () => {
        setLoadingHistory(true);
        try {
            const res = await fetch('/api/imports');
            const data = await res.json();
            setImportsHistory(Array.isArray(data) ? data : []);
        } catch (err) { console.error(err); }
        finally { setLoadingHistory(false); }
    };

    const resetState = () => {
        setFile(null); setIdImport(null); setTempPath(null);
        setAnalysis(null); setPipelineResult(null); setError(null);
        setUploading(false); setProcessing(false); setIngesting(false);
        setMode('add'); setIdColumn(''); setTargetColumn('');
    };

    const handleClose = () => { resetState(); onClose(); };

    // STEP 1: Upload & Analyze
    const handleUpload = async () => {
        if (!file) return;
        setUploading(true); setError(null);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', mode);
        try {
            const res = await fetch('/api/upload/dynamic', { method: 'POST', body: formData });
            const data = await res.json();
            if (res.ok) {
                setIdImport(data.id_import);
                setTempPath(data.temp_path);
                setAnalysis(data.analysis);
                // Auto-select suggested columns
                if (data.analysis.suggested_id_column) setIdColumn(data.analysis.suggested_id_column);
                if (data.analysis.suggested_target_column) setTargetColumn(data.analysis.suggested_target_column);
                setActiveTab(STEPS.CONFIG);
            } else { setError(data.error || "Upload failed"); }
        } catch (err) { setError(err.message); }
        finally { setUploading(false); }
    };

    // STEP 2: Ingest configured data
    const handleIngest = async () => {
        if (!idImport || !targetColumn) return;
        setIngesting(true); setError(null);
        try {
            const res = await fetch('/api/pipeline/ingest-dynamic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_import: idImport, temp_path: tempPath, id_column: idColumn, target_column: targetColumn, mode })
            });
            const data = await res.json();
            if (res.ok) {
                setActiveTab(STEPS.PROCESS);
            } else { setError(data.error || "Ingestion failed"); }
        } catch (err) { setError(err.message); }
        finally { setIngesting(false); }
    };

    // STEP 3: Run ML Pipeline
    const runPipeline = async () => {
        if (!idImport) return;
        setProcessing(true); setError(null);
        try {
            const res = await fetch(`/api/pipeline/run-dynamic/${idImport}`, { method: 'POST' });
            const data = await res.json();
            if (res.ok) {
                setPipelineResult(data);
                if (onPipelineComplete) onPipelineComplete();
            } else { setError(data.error || "Pipeline failed"); }
        } catch (err) { setError(err.message); }
        finally { setProcessing(false); }
    };

    const deleteImport = async (id) => {
        try {
            const res = await fetch(`/api/imports/${id}`, { method: 'DELETE' });
            if (res.ok) { setConfirmingDelete(null); fetchHistory(); if (onPipelineComplete) onPipelineComplete(); }
        } catch (err) { console.error(err); }
    };

    if (!isOpen) return null;

    const numericCols = analysis?.columns?.filter(c => c.dtype === 'numeric') || [];
    const textCols = analysis?.columns?.filter(c => c.dtype === 'text') || [];
    const allCols = analysis?.columns || [];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={handleClose}>
            <div className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl mx-4 overflow-hidden flex flex-col max-h-[92vh]" onClick={e => e.stopPropagation()}>

                {/* Header */}
                <div className="px-6 py-5 border-b border-slate-100 bg-gradient-to-r from-indigo-50 via-white to-fuchsia-50 shrink-0">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-gradient-to-br from-indigo-600 to-fuchsia-600 rounded-xl text-white shadow-lg shadow-indigo-500/20">
                                <Database size={20} />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-slate-800">Pipeline d'Intégration</h2>
                                <p className="text-xs text-slate-500">Importation dynamique, Configuration et Prédiction IA</p>
                            </div>
                        </div>
                        <button onClick={handleClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition"><X size={20} /></button>
                    </div>

                    {/* Tabs */}
                    <div className="flex gap-2 p-1 bg-slate-100/80 rounded-2xl w-fit">
                        {[
                            { id: STEPS.UPLOAD, icon: <Upload size={15} />, label: '1. Upload' },
                            { id: STEPS.CONFIG, icon: <Settings2 size={15} />, label: '2. Config', disabled: !analysis },
                            { id: STEPS.PROCESS, icon: <Play size={15} />, label: '3. IA', disabled: !idImport || activeTab === STEPS.UPLOAD },
                            { id: STEPS.HISTORY, icon: <History size={15} />, label: 'Historique' },
                        ].map(tab => (
                            <button key={tab.id} onClick={() => !tab.disabled && setActiveTab(tab.id)}
                                disabled={tab.disabled}
                                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${activeTab === tab.id ? 'bg-white text-indigo-600 shadow-sm' : tab.disabled ? 'text-slate-300 cursor-not-allowed' : 'text-slate-500 hover:text-slate-700'}`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Body */}
                <div className="p-6 overflow-y-auto flex-1">

                    {/* STEP 1: UPLOAD */}
                    {activeTab === STEPS.UPLOAD && (
                        <div className="space-y-5">
                            {/* Mode selection */}
                            <div className="flex gap-3">
                                {[
                                    { val: 'add', label: 'Ajout', desc: 'Empiler sur les données existantes', color: 'indigo' },
                                    { val: 'replace', label: 'Remplacement', desc: 'Remplacer les données dynamiques', color: 'amber' },
                                ].map(m => (
                                    <button key={m.val} onClick={() => setMode(m.val)}
                                        className={`flex-1 p-4 rounded-2xl border-2 text-left transition-all ${mode === m.val ? `border-${m.color}-400 bg-${m.color}-50/50 ring-2 ring-${m.color}-100` : 'border-slate-200 hover:border-slate-300'}`}
                                    >
                                        <p className="font-bold text-sm text-slate-800">{m.label}</p>
                                        <p className="text-xs text-slate-500 mt-0.5">{m.desc}</p>
                                    </button>
                                ))}
                            </div>

                            <div className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${dragActive ? 'border-indigo-400 bg-indigo-50/30' : 'border-slate-200 hover:border-indigo-300'}`}
                                onDragOver={e => { e.preventDefault(); setDragActive(true); }}
                                onDragLeave={() => setDragActive(false)}
                                onDrop={e => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); }}
                                onClick={() => inputRef.current?.click()}
                            >
                                <input ref={inputRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={e => setFile(e.target.files[0])} />
                                {file ? (
                                    <div className="flex flex-col items-center gap-2">
                                        <FileSpreadsheet size={40} className="text-emerald-500" />
                                        <p className="font-bold text-slate-800">{file.name}</p>
                                        <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} Ko</p>
                                        <button onClick={e => { e.stopPropagation(); setFile(null); }} className="text-rose-500 text-xs font-bold hover:underline">Changer</button>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <div className="mx-auto w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400"><Upload size={28} /></div>
                                        <p className="font-medium text-slate-600">Glissez votre fichier ici</p>
                                        <p className="text-xs text-slate-400">CSV, XLSX, XLS — Structure quelconque</p>
                                    </div>
                                )}
                            </div>

                            {error && <div className="p-3 bg-rose-50 border border-rose-100 rounded-2xl flex gap-2 text-rose-700 text-sm"><AlertCircle size={18} className="shrink-0 mt-0.5" /><p>{error}</p></div>}

                            <div className="flex justify-end">
                                <button onClick={handleUpload} disabled={!file || uploading}
                                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-fuchsia-600 text-white font-bold rounded-2xl shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center gap-2"
                                >
                                    {uploading ? <Loader2 className="animate-spin" size={18} /> : <ArrowRight size={18} />}
                                    Analyser le fichier
                                </button>
                            </div>
                        </div>
                    )}

                    {/* STEP 2: CONFIGURATION */}
                    {activeTab === STEPS.CONFIG && analysis && (
                        <div className="space-y-6">
                            {/* File summary */}
                            <div className="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 flex items-center gap-4">
                                <FileSpreadsheet size={32} className="text-indigo-500" />
                                <div>
                                    <p className="font-bold text-slate-800">{analysis.total_rows} lignes × {analysis.total_columns} colonnes</p>
                                    <p className="text-xs text-slate-500">Colonnes numériques : {numericCols.length} — Colonnes texte : {textCols.length}</p>
                                </div>
                            </div>

                            {/* Column selectors */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-sm font-bold text-slate-700">
                                        <Columns3 size={16} className="text-indigo-500" /> Colonne identifiant
                                    </label>
                                    <select value={idColumn} onChange={e => setIdColumn(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm font-medium focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none bg-white"
                                    >
                                        <option value="">— Aucun (auto-index) —</option>
                                        {allCols.map(c => (
                                            <option key={c.name} value={c.name}>{c.name} ({c.dtype}, {c.unique_values} uniques)</option>
                                        ))}
                                    </select>
                                    <p className="text-[10px] text-slate-400">Ex: Code Massar, Matricule, ID...</p>
                                </div>
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-sm font-bold text-slate-700">
                                        <Target size={16} className="text-fuchsia-500" /> Colonne cible (à prédire)
                                    </label>
                                    <select value={targetColumn} onChange={e => setTargetColumn(e.target.value)}
                                        className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm font-medium focus:ring-2 focus:ring-fuchsia-200 focus:border-fuchsia-400 outline-none bg-white"
                                    >
                                        <option value="">— Sélectionner —</option>
                                        {numericCols.map(c => (
                                            <option key={c.name} value={c.name}>{c.name} (moy: {c.sample_values.join(', ')})</option>
                                        ))}
                                    </select>
                                    <p className="text-[10px] text-slate-400">Colonne numérique que le modèle IA va prédire</p>
                                </div>
                            </div>

                            {/* Preview Table */}
                            <div>
                                <h4 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-2"><Table2 size={16} /> Prévisualisation (5 premières lignes)</h4>
                                <div className="overflow-x-auto rounded-2xl border border-slate-200">
                                    <table className="w-full text-xs">
                                        <thead>
                                            <tr className="bg-slate-50">
                                                {allCols.map(c => (
                                                    <th key={c.name} className={`px-3 py-2 text-left font-bold whitespace-nowrap ${c.name === targetColumn ? 'bg-fuchsia-50 text-fuchsia-700' : c.name === idColumn ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600'}`}>
                                                        {c.name}
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {analysis.preview.map((row, i) => (
                                                <tr key={i} className="border-t border-slate-100 hover:bg-slate-50">
                                                    {allCols.map(c => (
                                                        <td key={c.name} className={`px-3 py-1.5 whitespace-nowrap ${c.name === targetColumn ? 'bg-fuchsia-50/30 font-bold' : c.name === idColumn ? 'bg-indigo-50/30' : ''}`}>
                                                            {String(row[c.name] ?? '')}
                                                        </td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {error && <div className="p-3 bg-rose-50 border border-rose-100 rounded-2xl flex gap-2 text-rose-700 text-sm"><AlertCircle size={18} /><p>{error}</p></div>}

                            <div className="flex justify-between">
                                <button onClick={() => { resetState(); setActiveTab(STEPS.UPLOAD); }}
                                    className="px-5 py-2.5 text-slate-600 font-bold rounded-xl hover:bg-slate-100 transition flex items-center gap-2"
                                ><ArrowLeft size={16} /> Retour</button>
                                <button onClick={handleIngest} disabled={!targetColumn || ingesting}
                                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-fuchsia-600 text-white font-bold rounded-2xl shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center gap-2"
                                >
                                    {ingesting ? <Loader2 className="animate-spin" size={18} /> : <ArrowRight size={18} />}
                                    Charger les données
                                </button>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: AI PROCESSING */}
                    {activeTab === STEPS.PROCESS && (
                        <div className="space-y-8 py-4">
                            {pipelineResult ? (
                                <div className="p-8 bg-gradient-to-br from-emerald-50 to-white rounded-3xl border border-emerald-100 space-y-6 shadow-lg shadow-emerald-500/5">
                                    <div className="flex flex-col items-center gap-4 text-center">
                                        <div className="p-4 bg-emerald-500 text-white rounded-full shadow-lg shadow-emerald-500/20"><CheckCircle2 size={32} /></div>
                                        <h3 className="text-2xl font-bold text-slate-800">Pipeline Terminé !</h3>
                                        <p className="text-slate-500">Le modèle a été entraîné et les prédictions sont prêtes.</p>
                                    </div>
                                    <div className="grid grid-cols-3 gap-3">
                                        <div className="bg-white p-4 rounded-2xl shadow-sm border border-emerald-100/50 text-center">
                                            <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Précision (R²)</p>
                                            <p className="text-2xl font-black text-emerald-600">{(pipelineResult.training.r2_score * 100).toFixed(1)}%</p>
                                        </div>
                                        <div className="bg-white p-4 rounded-2xl shadow-sm border border-emerald-100/50 text-center">
                                            <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Erreur (MAE)</p>
                                            <p className="text-2xl font-black text-slate-800">{pipelineResult.training.mae}</p>
                                        </div>
                                        <div className="bg-white p-4 rounded-2xl shadow-sm border border-emerald-100/50 text-center">
                                            <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Prédictions</p>
                                            <p className="text-2xl font-black text-slate-800">{pipelineResult.predictions_count}</p>
                                        </div>
                                    </div>

                                    {/* Top Features */}
                                    {pipelineResult.training.top_features && (
                                        <div>
                                            <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3">Top Facteurs d'Influence</h4>
                                            <div className="space-y-2">
                                                {pipelineResult.training.top_features.slice(0, 5).map((f, i) => (
                                                    <div key={i} className="flex items-center gap-3">
                                                        <span className="text-xs font-bold text-slate-500 w-20 truncate">{f.name}</span>
                                                        <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                                                            <div className="h-full bg-gradient-to-r from-indigo-500 to-fuchsia-500 rounded-full transition-all" style={{ width: `${(f.importance * 100 / (pipelineResult.training.top_features[0]?.importance || 1))}%` }} />
                                                        </div>
                                                        <span className="text-xs font-black text-slate-600 w-12 text-right">{(f.importance * 100).toFixed(1)}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <button onClick={handleClose} className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-xl transition-all active:scale-[0.98]">
                                        Fermer et Voir les Résultats
                                    </button>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-6 text-center">
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-600 border border-emerald-200"><CheckCircle2 size={24} /></div>
                                        <div className="h-0.5 w-10 bg-slate-200" />
                                        <div className="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-600 border border-emerald-200"><Settings2 size={24} /></div>
                                        <div className="h-0.5 w-10 bg-slate-200" />
                                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border ${processing ? 'bg-indigo-50 text-indigo-600 border-indigo-200 animate-pulse' : 'bg-slate-50 text-slate-300 border-slate-100'}`}><Play size={24} /></div>
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-800">Données chargées avec succès</h3>
                                        <p className="text-sm text-slate-500 mt-1">Cliquez pour lancer l'entraînement IA et générer les prédictions.</p>
                                    </div>

                                    {error && <div className="p-3 bg-rose-50 border border-rose-100 rounded-2xl flex gap-2 text-rose-700 text-sm w-full"><AlertCircle size={18} /><p>{error}</p></div>}

                                    <button onClick={runPipeline} disabled={processing}
                                        className="w-full py-4 bg-slate-900 text-white font-bold rounded-2xl hover:bg-slate-800 shadow-xl active:scale-[0.98] transition-all flex items-center justify-center gap-3 text-lg disabled:opacity-75"
                                    >
                                        {processing ? <><Loader2 className="animate-spin" /> Entraînement en cours...</> : <><Play fill="currentColor" /> Lancer le Pipeline IA</>}
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {/* HISTORY TAB */}
                    {activeTab === STEPS.HISTORY && (
                        <div className="space-y-3">
                            {loadingHistory ? (
                                <div className="flex flex-col items-center py-16 gap-3 text-slate-400"><Loader2 className="animate-spin" size={32} /><p className="font-medium">Chargement...</p></div>
                            ) : importsHistory.length === 0 ? (
                                <div className="text-center py-16 text-slate-400">
                                    <LayoutList size={48} className="mx-auto mb-3 opacity-20" />
                                    <p className="font-bold text-slate-600">Aucun import trouvé</p>
                                    <p className="text-sm text-slate-400 mt-1">Importez un fichier pour commencer.</p>
                                </div>
                            ) : (
                                importsHistory.map(imp => (
                                    <div key={imp.id_import} className="group p-4 bg-slate-50 hover:bg-white border hover:border-indigo-200 rounded-2xl transition-all flex items-center justify-between shadow-sm hover:shadow-md">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2.5 bg-white group-hover:bg-indigo-50 rounded-xl text-slate-400 group-hover:text-indigo-500 transition shadow-sm"><FileSpreadsheet size={18} /></div>
                                            <div>
                                                <h4 className="font-bold text-sm text-slate-800 flex items-center gap-2">
                                                    {imp.filename}
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider ${imp.status === 'Predicted' ? 'bg-emerald-100 text-emerald-600' : imp.status === 'Error' ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-600'}`}>
                                                        {imp.status}
                                                    </span>
                                                    {imp.is_dynamic && <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-600">Dynamique</span>}
                                                </h4>
                                                <div className="flex items-center gap-3 text-xs text-slate-500">
                                                    <span className="flex items-center gap-1"><Calendar size={12} /> {new Date(imp.upload_date).toLocaleDateString()}</span>
                                                    <span className="flex items-center gap-1"><LayoutList size={12} /> {imp.row_count} lignes</span>
                                                    {imp.target_column && <span className="flex items-center gap-1"><Target size={12} /> {imp.target_column}</span>}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {confirmingDelete === imp.id_import ? (
                                                <div className="flex gap-1.5">
                                                    <button onClick={() => deleteImport(imp.id_import)} className="px-3 py-1.5 bg-rose-500 text-white text-xs font-bold rounded-lg hover:bg-rose-600 transition">Oui</button>
                                                    <button onClick={() => setConfirmingDelete(null)} className="px-3 py-1.5 bg-slate-100 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-200 transition">Non</button>
                                                </div>
                                            ) : (
                                                <button onClick={() => setConfirmingDelete(imp.id_import)} className="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition"><Trash2 size={18} /></button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-between items-center text-[10px] uppercase tracking-widest font-bold text-slate-400 shrink-0">
                    <span>Mode: {mode === 'add' ? 'Ajout' : 'Remplacement'}</span>
                    <span>v3.0 — Pipeline Dynamique</span>
                </div>
            </div>
        </div>
    );
}
