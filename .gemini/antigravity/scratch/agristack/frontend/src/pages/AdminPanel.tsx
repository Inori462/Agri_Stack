import React from 'react';
import { useTranslation } from 'react-i18next';

const AdminPanel: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('adminPanel')}</h2>
      <p className="text-gray-700">Admin functionalities will be added here.</p>
    </div>
  );
};

export default AdminPanel;
