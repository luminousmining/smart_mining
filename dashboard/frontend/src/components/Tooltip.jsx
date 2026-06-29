import { useState } from 'react';

/**
 * Lightweight hover-card. Wraps a trigger (`children`) and shows `content`
 * in a styled floating box on hover. Uses `position: fixed` (anchored to the
 * trigger's bounding rect) so it is never clipped by an overflow container.
 */
export default function Tooltip({ children, content }) {
  const [pos, setPos] = useState(null); // { top, left } or null when hidden

  const show = (e) => {
    if (!content) return;
    const r = e.currentTarget.getBoundingClientRect();
    setPos({ top: r.bottom + 6, left: r.left });
  };
  const hide = () => setPos(null);

  return (
    <span
      style={s.trigger}
      onMouseEnter={show}
      onMouseLeave={hide}
    >
      {children}
      {pos && (
        <div style={{ ...s.box, top: pos.top, left: pos.left }}>
          {content}
        </div>
      )}
    </span>
  );
}

const s = {
  trigger: { display: 'inline-block' },
  box: {
    position: 'fixed',
    zIndex: 1000,
    background: '#0d0e1a',
    border: '1px solid #2a2c45',
    borderRadius: 8,
    padding: '8px 10px',
    fontSize: 12,
    boxShadow: '0 6px 20px rgba(0, 0, 0, 0.45)',
    pointerEvents: 'none',
    whiteSpace: 'nowrap',
  },
};
