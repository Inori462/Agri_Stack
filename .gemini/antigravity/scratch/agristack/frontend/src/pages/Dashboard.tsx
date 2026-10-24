import React from 'react';
import DonutChart from '@/components/DonutChart';
import { useTranslation } from 'react-i18next';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('dashboard')}</h2>
      <DonutChart />
    </div>
  );
};

export default Dashboard;
