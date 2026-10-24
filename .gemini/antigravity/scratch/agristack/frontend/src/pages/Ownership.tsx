import React from 'react';
import { useTranslation } from 'react-i18next';

const Ownership: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('ownership')}</h2>
      <p className="text-gray-700">Ownership management UI coming soon.</p>
    </div>
  );
};

export default Ownership;
