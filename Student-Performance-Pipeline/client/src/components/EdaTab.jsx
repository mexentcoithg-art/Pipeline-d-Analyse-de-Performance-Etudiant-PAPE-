import React, { useState } from 'react';
import { BarChart3, Download, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function EdaTab() {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(false);
    const [timestamp, setTimestamp] = useState(Date.now());

    const handleRefresh = () => {
        setLoading(true);
        setTimestamp(Date.now());
        setTimeout(() => setLoading(false), 800);
    };

    const imageUrl = `/api/eda/heatmap?t=${timestamp}`;

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Header Actions */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div>
                    <h2 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-amber-500 to-rose-600 tracking-tight flex items-center gap-3">
                        <BarChart3 className="text-amber-500" size={28} />
                        {t('eda.header.title')}
                    </h2>
                    <p className="text-slate-500 mt-1 max-w-xl">
                        {t('eda.header.subtitle')}
                    </p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={handleRefresh}
                        className="px-5 py-2.5 bg-white border border-slate-200 hover:border-amber-400 hover:bg-amber-50 text-slate-700 hover:text-amber-700 font-bold rounded-xl transition-all duration-300 shadow-sm hover:shadow-md flex items-center gap-2 text-sm"
                    >
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                        {t('eda.actions.regenerate')}
                    </button>
                </div>
            </div>

            {/* Heatmap Image Container */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 flex flex-col items-center justify-center min-h-[500px] relative">
                {loading ? (
                    <div className="animate-pulse space-y-4 flex flex-col items-center">
                        <div className="w-12 h-12 border-4 border-slate-200 border-t-amber-500 rounded-full animate-spin"></div>
                        <p className="text-slate-500 font-medium">{t('eda.chart.loading')}</p>
                    </div>
                ) : (
                    <div className="w-full flex-1 flex items-center justify-center">
                        <img
                            src={imageUrl}
                            alt="Correlation Heatmap"
                            className="max-w-full max-h-[700px] rounded-xl object-contain shadow-sm border border-slate-200"
                            onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.parentElement.innerHTML = '<div class="text-slate-400 text-center p-12">Failed to load heatmap from Python backend.<br/>Ensure /api/eda/heatmap is implemented.</div>';
                            }}
                        />
                    </div>
                )}
            </div>

        </div>
    );
}
