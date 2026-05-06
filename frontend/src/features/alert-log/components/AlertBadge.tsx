import type { AlertSeverity, AlertStatus } from '../model/alertLogData';
import { severityClassNames, statusClassNames } from '../model/alertLogData';

type AlertBadgeProps = {
  type: 'severity';
  value: AlertSeverity;
} | {
  type: 'status';
  value: AlertStatus;
};

export function AlertBadge(props: AlertBadgeProps) {
  const className = props.type === 'severity' ? severityClassNames[props.value] : statusClassNames[props.value];

  return <span className={`inline-grid h-11 min-w-[78px] place-items-center rounded-lg px-4 text-[19px] font-black tracking-[-0.04em] ${className}`}>{props.value}</span>;
}
