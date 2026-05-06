import React from 'react';
import { Info, Code, Database, BrainCircuit, Users, ExternalLink, ShieldCheck, Zap, BarChart2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function AboutTab({ darkMode }) {
    const { t } = useTranslation();

    const technologies = [
        { name: 'React JS & Vite', icon: <Code className="text-cyan-500" />, desc: 'Frontend UI Library' },
        { name: 'Python & Flask', icon: <Zap className="text-yellow-500" />, desc: 'Backend REST API' },
        { name: 'Scikit-Learn (IA)', icon: <BrainCircuit className="text-fuchsia-500" />, desc: 'Machine Learning Models' },
        { name: 'PostgreSQL', icon: <Database className="text-indigo-500" />, desc: 'Relational DB & JSONB' },
        { name: 'Power BI', icon: <BarChart2 className="text-amber-500" />, desc: 'Business Intelligence' },
    ];

    const features = [
        { title: t('about.features.realtime'), desc: t('about.features.realtimeDesc') },
        { title: t('about.features.ai'), desc: t('about.features.aiDesc') },
        { title: t('about.features.i18n'), desc: t('about.features.i18nDesc') },
        { title: t('about.features.responsive'), desc: t('about.features.responsiveDesc') },
    ];

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-fuchsia-700 p-12 text-white shadow-2xl">
                <div className="relative z-10 max-w-3xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-[10px] font-bold uppercase tracking-widest mb-6">
                        <Info size={14} /> {t('about.hero.subtitle')}
                    </div>
                    <h1 className="text-5xl font-black tracking-tight mb-6 leading-tight">
                        Student Performance <br />
                        <span className="text-fuchsia-300">Pipeline & IA</span>
                    </h1>
                    <p className="text-lg text-indigo-100 font-medium leading-relaxed mb-8">
                        {t('about.hero.description')}
                    </p>
                </div>

                {/* Decorative elements */}
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 right-0 translate-y-1/4 translate-x-1/4 w-64 h-64 bg-fuchsia-400/20 rounded-full blur-3xl"></div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Project Info */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                        <h2 className="text-2xl font-black text-slate-800 dark:text-slate-100 mb-6 flex items-center gap-3">
                            <Users className="text-indigo-500" />
                            {t('about.mission.title')}
                        </h2>
                        <div className="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 leading-relaxed space-y-4">
                            <p>{t('about.mission.p1')}</p>
                            <p>{t('about.mission.p2')}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {features.map((feature, i) => (
                            <div key={i} className="bg-slate-50 dark:bg-slate-800/40 rounded-2xl p-6 border border-slate-100 dark:border-slate-700/50">
                                <h3 className="font-black text-slate-800 dark:text-slate-100 text-sm uppercase tracking-wider mb-2">{feature.title}</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Tech Stack */}
                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 border border-slate-100 dark:border-slate-800 shadow-sm h-full">
                        <h2 className="text-xl font-black text-slate-800 dark:text-slate-100 mb-8 flex items-center gap-3">
                            <Database className="text-fuchsia-500" />
                            {t('about.tech.title')}
                        </h2>
                        <div className="space-y-6">
                            {technologies.map((tech, i) => (
                                <div key={i} className="flex items-center gap-4 group cursor-default">
                                    <div className="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-800 flex items-center justify-center border border-slate-100 dark:border-slate-700 group-hover:scale-110 transition-transform">
                                        {tech.icon}
                                    </div>
                                    <div>
                                        <h4 className="font-black text-slate-800 dark:text-slate-100 text-sm">{tech.name}</h4>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{tech.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-12 pt-8 border-t border-slate-100 dark:border-slate-800">
                            <a
                                href="https://github.com"
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center justify-center gap-2 w-full py-4 bg-slate-900 dark:bg-slate-800 text-white rounded-2xl font-black uppercase tracking-widest text-[10px] hover:bg-slate-800 dark:hover:bg-slate-700 transition-colors shadow-lg shadow-slate-900/10"
                            >
                                <ExternalLink size={14} />
                                {t('about.tech.repo')}
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer Info */}
            <footer className="text-center py-10 opacity-50">
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 dark:text-slate-500">
                    © {new Date().getFullYear()} — Student Performance Pipeline — PFE Project
                </p>
            </footer>
        </div>
    );
}
