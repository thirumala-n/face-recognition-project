import React from 'react';

const COLOR_MAPS = {
  indigo: {
    bg: 'bg-indigo-50',
    text: 'text-indigo-600',
    border: 'border-indigo-100',
  },
  emerald: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-600',
    border: 'border-emerald-100',
  },
  rose: {
    bg: 'bg-rose-50',
    text: 'text-rose-600',
    border: 'border-rose-100',
  },
  amber: {
    bg: 'bg-amber-50',
    text: 'text-amber-600',
    border: 'border-amber-100',
  },
  blue: {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    border: 'border-blue-100',
  },
};

export default function StatCard({
  title,
  value,
  icon: Icon,
  color = 'indigo',
  subtext,
  badgeText,
}) {
  const styles = COLOR_MAPS[color] || COLOR_MAPS.indigo;

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-lg ${styles.bg} ${styles.text}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold tracking-tight text-slate-900">
          {value !== undefined && value !== null ? value : '—'}
        </span>
        {badgeText && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles.bg} ${styles.text}`}>
            {badgeText}
          </span>
        )}
      </div>
      {subtext && (
        <p className="mt-2 text-xs text-slate-500 font-normal">
          {subtext}
        </p>
      )}
    </div>
  );
}
