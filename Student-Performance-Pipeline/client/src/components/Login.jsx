import React, { useState } from 'react';
import { LogIn, ShieldAlert, Lock, User, Activity } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function Login({ onLogin, darkMode }) {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                onLogin(data.user);
            } else {
                setError(data.error || (t('login.error_invalid') || 'Identifiants incorrects'));
                setIsLoading(false);
            }
        } catch (err) {
            console.error('[LOGIN FETCH ERROR]', err, 'URL:', window.location.hostname === 'localhost' ? 'http://127.0.0.1:5000' : `http://${window.location.hostname}:5000`);
            setError(t('login.error_server') || 'Erreur de connexion au serveur');
            setIsLoading(false);
        }
    };

    return (
        <div className={`min-h-screen flex items-center justify-center p-6 bg-slate-50 dark:bg-slate-950 transition-colors duration-500 overflow-hidden relative`}>
            {/* Background Blobs */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[100px] animate-blob"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-fuchsia-500/10 dark:bg-fuchsia-500/5 rounded-full blur-[100px] animate-blob animation-delay-2000"></div>

            <div className="w-full max-w-md relative z-10 animate-in fade-in zoom-in duration-500">
                <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-2xl shadow-indigo-500/10 border border-slate-100 dark:border-slate-800 p-10 overflow-hidden">
                    {/* Header */}
                    <div className="text-center mb-10">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 to-fuchsia-600 text-white mb-6 shadow-xl shadow-indigo-500/20 animate-pulse">
                            <Activity size={40} />
                        </div>
                        <h1 className="text-3xl font-black text-slate-800 dark:text-white tracking-tight leading-tight">
                            {t('login.title') || 'Bon retour !'}
                        </h1>
                        <p className="text-slate-400 dark:text-slate-500 font-bold uppercase tracking-[0.2em] text-[10px] mt-2">
                            {t('login.subtitle') || 'Student Performance Pipeline'}
                        </p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">
                                {t('login.username') || 'Utilisateur'}
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                                    <User size={18} />
                                </div>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-2xl text-slate-800 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium"
                                    placeholder="admin"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">
                                {t('login.password') || 'Mot de passe'}
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                                    <Lock size={18} />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-2xl text-slate-800 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="flex items-center gap-3 p-4 bg-rose-50 dark:bg-rose-500/10 border border-rose-100 dark:border-rose-500/20 rounded-2xl text-rose-600 dark:text-rose-400 text-xs font-bold animate-in slide-in-from-top-2">
                                <ShieldAlert size={16} />
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white rounded-2xl font-black uppercase tracking-[0.2em] text-xs shadow-xl shadow-indigo-500/20 transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 flex items-center justify-center gap-2 group"
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    <LogIn size={18} className="group-hover:translate-x-1 transition-transform" />
                                    {t('login.button') || 'Se connecter'}
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer Info */}
                    <p className="mt-8 text-center text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-relaxed">
                        {t('login.security_tip') || 'Système sécurisé • Portée restreinte'}
                    </p>
                </div>
            </div>
        </div>
    );
}
