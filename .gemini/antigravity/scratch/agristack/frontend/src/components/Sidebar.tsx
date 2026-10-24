import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const navItems = [
  { path: '/dashboard', labelKey: 'dashboard' },
  { path: '/my-farms', labelKey: 'myFarms' },
  { path: '/ownership', labelKey: 'ownership' },
  { path: '/marketplace', labelKey: 'marketplace' },
  { path: '/settlement', labelKey: 'settlement' },
  { path: '/admin', labelKey: 'adminPanel' },
];

const Sidebar: React.FC = () => {
  const { t } = useTranslation();
  return (
    <aside className="w-64 bg-white border-r p-4 flex flex-col">
      <h2 className="text-xl font-bold mb-6">AgriStack</h2>
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block px-3 py-2 rounded hover:bg-gray-100 ${isActive ? 'bg-gray-200 font-medium' : ''}`
            }
          >
            {t(item.labelKey)}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
