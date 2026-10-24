import React from 'react';
import { useTranslation } from 'react-i18next';

const Settlement: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('settlement')}</h2>
      <p className="text-gray-700">Settlement details will be displayed here.</p>
    </div>
  );
};

export default Settlement;
