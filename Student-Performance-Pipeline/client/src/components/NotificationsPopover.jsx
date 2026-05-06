import React, { useState, useEffect } from 'react';
import { Bell, Check, Info, AlertCircle, X } from 'lucide-react';

export default function NotificationsPopover({ API_BASE_URL, user }) {
    const [alerts, setAlerts] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    const fetchAlerts = async () => {
        try {
            let url = `${API_BASE_URL}/api/alerts`;
            const params = new URLSearchParams();
            if (user?.role) params.append('role', user.role);
            if (user?.class_assigned) params.append('class_name', user.class_assigned);

            if (params.toString()) {
                url += `?${params.toString()}`;
            }

            const res = await fetch(url);
            const data = await res.json();
            if (Array.isArray(data)) {
                setAlerts(data);
                setUnreadCount(data.filter(a => !a.is_read).length);
            }
        } catch (err) {
            console.error("Alerts fetch error:", err);
        }
    };

    useEffect(() => {
        if (user) {
            fetchAlerts();
            const interval = setInterval(fetchAlerts, 60000); // Check every minute
            return () => clearInterval(interval);
        }
    }, [user]);

    const markAsRead = async (id) => {
        try {
            await fetch(`${API_BASE_URL}/api/alerts/${id}/read`, { method: 'PUT' });
            fetchAlerts();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2.5 bg-slate-100/80 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all shadow-sm group"
            >
                <Bell size={20} className={unreadCount > 0 ? "animate-swing" : ""} />
                {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-500 text-white text-[10px] font-black rounded-full flex items-center justify-center border-2 border-white dark:border-slate-950">
                        {unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <>
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    ></div>
                    <div className="absolute right-0 mt-3 w-80 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-800 z-50 overflow-hidden animate-in slide-in-from-top-2 duration-200">
                        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/50">
                            <h3 className="text-sm font-black text-slate-800 dark:text-white uppercase tracking-wider">Notifications</h3>
                            <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-slate-600">
                                <X size={16} />
                            </button>
                        </div>

                        <div className="max-h-96 overflow-y-auto custom-scrollbar">
                            {alerts.length === 0 ? (
                                <div className="p-8 text-center text-slate-400">
                                    <Info className="mx-auto mb-2 opacity-20" size={32} />
                                    <p className="text-xs font-bold uppercase tracking-widest">Aucune alerte</p>
                                </div>
                            ) : (
                                alerts.map((alert) => (
                                    <div
                                        key={alert.id_alert}
                                        className={`p-4 border-b border-slate-50 dark:border-slate-800 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors relative ${!alert.is_read ? 'bg-indigo-50/30 dark:bg-indigo-500/5' : ''}`}
                                    >
                                        <div className="flex gap-3">
                                            <div className="mt-1">
                                                <AlertCircle size={16} className="text-rose-500" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight mb-1">
                                                    {alert.message}
                                                </p>
                                                <p className="text-[10px] text-slate-400 font-medium">
                                                    {new Date(alert.date_creation).toLocaleString()}
                                                </p>
                                            </div>
                                            {!alert.is_read && (
                                                <button
                                                    onClick={() => markAsRead(alert.id_alert)}
                                                    className="p-1 text-indigo-500 hover:bg-indigo-100 rounded-lg transition-colors"
                                                    title="Marquer comme lu"
                                                >
                                                    <Check size={14} />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        {alerts.length > 0 && (
                            <div className="p-3 text-center bg-slate-50 dark:bg-slate-800/30">
                                <button className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-[0.2em] hover:underline">
                                    Voir tout l'historique
                                </button>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
