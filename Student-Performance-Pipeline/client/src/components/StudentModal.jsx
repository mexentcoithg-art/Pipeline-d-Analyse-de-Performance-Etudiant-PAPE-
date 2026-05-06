import React, { useEffect, useState } from 'react';
import { X, User, Activity, GraduationCap, MapPin, Loader2, MessageSquarePlus, History, ClipboardCheck, Trash2, Edit3, Save, FileDown, Target } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function StudentModal({ studentId, onClose }) {
    const { t } = useTranslation();
    const [data, setData] = useState(null);
    const [interventions, setInterventions] = useState([]);
    const [orientation, setOrientation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({});
    const [newAction, setNewAction] = useState({ type_action: '', description: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

    const fetchInterventions = () => {
        const API_BASE_URL = '';
        fetch(`${API_BASE_URL}/api/interventions/${studentId}`)
            .then(res => res.json())
            .then(data => setInterventions(Array.isArray(data) ? data : []))
            .catch(err => console.error("Interventions fetch error:", err));
    };

    useEffect(() => {
        if (!studentId) return;
        setLoading(true);
        const API_BASE_URL = '';

        Promise.all([
            fetch(`${API_BASE_URL}/api/students/${studentId}`).then(res => res.json()),
            fetch(`${API_BASE_URL}/api/interventions/${studentId}`).then(res => res.json())
        ])
            .then(([studentData, interventionsData]) => {
                setData(studentData);
                setInterventions(Array.isArray(interventionsData) ? interventionsData : []);

                // Fetch orientation based on massar_code if available
                if (studentData && studentData.massar_code) {
                    fetch(`${API_BASE_URL}/api/analytics/orientation/${studentData.massar_code}`)
                        .then(res => res.json())
                        .then(orientData => setOrientation(orientData))
                        .catch(err => console.error("Orientation Fetch Error:", err));
                }

                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [studentId]);

    const handleAddIntervention = async (e) => {
        e.preventDefault();
        if (!newAction.type_action) return;

        setIsSubmitting(true);
        const API_BASE_URL = '';

        try {
            const res = await fetch(`${API_BASE_URL}/api/interventions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_etudiant: studentId,
                    type_action: newAction.type_action,
                    description: newAction.description,
                    id_user: currentUser.id,
                    status_efficacite: 'En cours'
                })
            });

            if (res.ok) {
                setNewAction({ type_action: '', description: '' });
                fetchInterventions();
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleUpdate = async () => {
        const API_BASE_URL = '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/students/${data.massar_code}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editData)
            });
            if (res.ok) {
                setIsEditing(false);
                setData({ ...data, ...editData });
            }
        } catch (err) { console.error(err); }
    };

    const handleDelete = async () => {
        if (!window.confirm("Supprimer cet étudiant ?")) return;
        const API_BASE_URL = '';
        try {
            const res = await fetch(`${API_BASE_URL}/api/students/${data.massar_code}`, { method: 'DELETE' });
            if (res.ok) onClose();
        } catch (err) { console.error(err); }
    };

    if (!studentId) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-md p-4 animate-in fade-in duration-200">
            <div className="bg-white rounded-3xl shadow-2xl shadow-indigo-900/20 w-full max-w-4xl overflow-hidden animate-in zoom-in-95 duration-300">

                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <h2 className="text-xl font-bold flex items-center gap-3 text-slate-800">
                        <div className="p-2 bg-gradient-to-br from-fuchsia-500 to-indigo-600 rounded-xl text-white shadow-md shadow-fuchsia-500/30">
                            <User size={20} />
                        </div>
                        {t('modal.title')}
                    </h2>
                    <div className="flex items-center gap-2">
                        {currentUser.role === 'Admin' && (
                            <>
                                {isEditing ? (
                                    <button onClick={handleUpdate} className="p-2 text-emerald-500 hover:bg-emerald-50 rounded-full transition" title="Sauvegarder">
                                        <Save size={20} />
                                    </button>
                                ) : (
                                    <button onClick={() => { setIsEditing(true); setEditData(data); }} className="p-2 text-indigo-500 hover:bg-indigo-50 rounded-full transition" title="Modifier">
                                        <Edit3 size={20} />
                                    </button>
                                )}
                                <button onClick={handleDelete} className="p-2 text-rose-500 hover:bg-rose-50 rounded-full transition" title="Supprimer">
                                    <Trash2 size={20} />
                                </button>
                                <div className="h-6 w-px bg-slate-200 mx-1"></div>
                            </>
                        )}
                        <button
                            onClick={() => window.open(`/api/reports/student/${data.massar_code}`, '_blank')}
                            className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-full transition"
                            title="Télécharger le rapport PDF"
                        >
                            <FileDown size={20} />
                        </button>
                        <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-full transition">
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[80vh]">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-48 text-indigo-500">
                            <Loader2 className="animate-spin mb-4" size={32} />
                            <p className="text-slate-500 font-medium">{t('modal.loading')}</p>
                        </div>
                    ) : data && !data.error ? (
                        <div className="space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Profile Card */}
                                <div className="space-y-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-16 h-16 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-2xl font-bold font-mono">
                                            {data.gender === 'M' ? '👦' : '👧'}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-slate-800">{t('modal.profile.id', { id: data.massar_code })}</h3>
                                            <p className="text-slate-500 flex items-center gap-1 text-sm">
                                                <GraduationCap size={14} /> {t('modal.profile.class', { class: data.class_name || 'N/A' })}
                                            </p>
                                            <p className="text-slate-500 flex items-center gap-1 text-sm mt-0.5">
                                                <MapPin size={14} /> {t('modal.profile.level', { level: data.level || 'N/A' })}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
                                        <h4 className="text-xs font-bold uppercase text-slate-400 mb-2">{t('modal.social.title')}</h4>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500">{t('modal.social.guardian')}</span>
                                            <span className="font-medium text-slate-800">{data.guardian_type || t('modal.social.guardianUnknown')}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500">{t('modal.social.schoolingYears')}</span>
                                            <span className="font-medium text-slate-800">{t('modal.social.years', { count: data.schooling_years })}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500">{t('modal.social.guardianJob')}</span>
                                            <span className="font-medium text-slate-800">{data.guardian2_job || t('modal.social.jobUnknown')}</span>
                                        </div>
                                    </div>

                                    {/* AI Orientation Recommendation */}
                                    <div className="bg-emerald-50 p-5 rounded-2xl border border-emerald-100 shadow-sm">
                                        <div className="flex items-start gap-3 mb-3">
                                            <div className="p-2 bg-white rounded-lg text-emerald-600 shadow-sm">
                                                <Target size={20} />
                                            </div>
                                            <div>
                                                <h4 className="text-sm font-black text-emerald-900 uppercase tracking-wider">Orientation Recommandée</h4>
                                                <p className="text-[10px] text-emerald-700 font-bold uppercase tracking-widest leading-none mt-1">Analyse Prédictive IA</p>
                                            </div>
                                        </div>

                                        {orientation ? (
                                            <div className="space-y-2">
                                                <div className="bg-white/80 backdrop-blur-sm p-3 rounded-xl border border-emerald-200">
                                                    <p className="text-xl font-black text-slate-800">{orientation.recommended_track}</p>
                                                    <p className="text-xs text-slate-500 font-medium mt-1">{orientation.interpretation}</p>
                                                </div>
                                            </div>
                                        ) : (
                                            <p className="text-emerald-700 text-xs font-medium animate-pulse">Calcul de l'orientation...</p>
                                        )}
                                    </div>
                                </div>

                                {/* Academic Stats */}
                                <div className="space-y-4">
                                    <h4 className="text-sm font-bold text-slate-800 border-b border-slate-100 pb-2">{t('modal.academic.title')}</h4>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100 text-center">
                                            <p className="text-xs text-emerald-600 font-bold uppercase mb-1">{t('modal.academic.finalAvg')}</p>
                                            <p className="text-2xl font-black text-emerald-700">{data.G3}/20</p>
                                        </div>
                                        <div className="bg-rose-50 p-4 rounded-xl border border-rose-100 text-center">
                                            <p className="text-xs text-rose-600 font-bold uppercase mb-1">{t('modal.academic.absences')}</p>
                                            <p className="text-2xl font-black text-rose-700">{data.absences}</p>
                                        </div>
                                    </div>
                                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-bold text-slate-600">{t('modal.academic.participation')}</span>
                                            <span className="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-600 to-indigo-600">{data.participation}/20</span>
                                        </div>
                                        <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                                            <div className="bg-gradient-to-r from-fuchsia-500 to-indigo-500 h-full rounded-full transition-all duration-1000" style={{ width: `${(data.participation / 20) * 100}%` }}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Interventions Section (RBAC Aware) */}
                            <div className="pt-6 border-t border-slate-100">
                                <h4 className="text-lg font-black text-slate-800 mb-6 flex items-center gap-2">
                                    <ClipboardCheck className="text-indigo-600" size={24} />
                                    Actions & Suivi Pédagogique
                                </h4>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                    {/* History */}
                                    <div className="md:col-span-2 space-y-4">
                                        <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                                            <History size={14} /> Historique des actions
                                        </div>
                                        {interventions.length === 0 ? (
                                            <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center text-slate-400">
                                                <p className="text-sm">Aucune action enregistrée pour le moment.</p>
                                            </div>
                                        ) : (
                                            <div className="space-y-3 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                                                {interventions.map((item, idx) => (
                                                    <div key={idx} className="bg-white border border-slate-100 rounded-2xl p-4 shadow-sm hover:border-indigo-200 transition-colors">
                                                        <div className="flex justify-between items-start mb-2">
                                                            <span className="px-2.5 py-1 bg-indigo-50 text-indigo-600 rounded-lg text-[10px] font-black uppercase tracking-wider">
                                                                {item.type_action}
                                                            </span>
                                                            <span className="text-[10px] text-slate-400 font-medium">
                                                                {new Date(item.date_action).toLocaleDateString()}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-slate-600 leading-relaxed mb-2">{item.description}</p>
                                                        <div className="flex items-center justify-between mt-3 text-[10px] font-bold">
                                                            <span className="text-slate-400 flex items-center gap-1 uppercase tracking-widest">
                                                                <User size={12} /> {item.creator_name}
                                                            </span>
                                                            <span className={`uppercase tracking-widest ${item.status_efficacite === 'Réussite' ? 'text-emerald-500' : 'text-amber-500'}`}>
                                                                {item.status_efficacite}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* Add New Action (Only for Enseignant & Admin) */}
                                    {(currentUser.role === 'Enseignant' || currentUser.role === 'Admin') && (
                                        <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100 flex flex-col">
                                            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                                                <MessageSquarePlus size={14} /> Nouvelle Action
                                            </div>
                                            <form onSubmit={handleAddIntervention} className="space-y-4 flex-1 flex flex-col">
                                                <select
                                                    value={newAction.type_action}
                                                    onChange={e => setNewAction({ ...newAction, type_action: e.target.value })}
                                                    className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all font-medium"
                                                    required
                                                >
                                                    <option value="">-- Type d'action --</option>
                                                    <option value="Entretien Parents">Entretien Parents</option>
                                                    <option value="Soutien Scolaire">Soutien Scolaire</option>
                                                    <option value="Avertissement">Avertissement</option>
                                                    <option value="Orientation">Orientation</option>
                                                </select>
                                                <textarea
                                                    placeholder="Détails de l'intervention..."
                                                    value={newAction.description}
                                                    onChange={e => setNewAction({ ...newAction, description: e.target.value })}
                                                    className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all font-medium resize-none flex-1 min-h-[100px]"
                                                />
                                                <button
                                                    type="submit"
                                                    disabled={isSubmitting || !newAction.type_action}
                                                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-all shadow-lg shadow-indigo-600/20 active:scale-95 disabled:opacity-50"
                                                >
                                                    {isSubmitting ? 'Envoi...' : 'Enregistrer'}
                                                </button>
                                            </form>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center text-rose-500 py-10">
                            <Activity className="mx-auto mb-2 opacity-50" size={32} />
                            <p>{t('modal.error')}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
