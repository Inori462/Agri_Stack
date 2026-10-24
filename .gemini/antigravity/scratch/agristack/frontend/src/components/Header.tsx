import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any auth tokens (placeholder)
    localStorage.removeItem('access_token');
    navigate('/');
  };

  return (
    <header className="flex items-center justify-between bg-white border-b p-4 shadow-sm">
      <h1 className="text-2xl font-semibold">AgriStack</h1>
      <button
        onClick={handleLogout}
        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
      >
        {t('logout')}
      </button>
    </header>
  );
};

export default Header;
