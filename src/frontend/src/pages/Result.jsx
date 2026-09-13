import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const { result, crop, preview } = location.state || {};

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center p-20">
        <h2 className="text-2xl font-bold text-error mb-4">No diagnosis data available.</h2>
        <button 
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-primary text-on-primary rounded-lg"
        >
          Return to Scanner
        </button>
      </div>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);
  const isHealthy = result.class_label.toLowerCase().includes('healthy');

  return (
    <div className="flex flex-col w-full max-w-7xl mx-auto px-gutter md:px-margin-tablet lg:px-margin-desktop py-space-lg">
      <div className="flex items-center gap-space-sm mb-space-lg">
        <button onClick={() => navigate('/')} className="flex items-center text-primary hover:bg-surface-container-low p-2 rounded-lg">
          <span className="material-symbols-outlined">arrow_back</span>
          <span className="ml-2 font-label-md">New Scan</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
        
        {/* Left Column: Result & Confidence */}
        <div className="lg:col-span-8 flex flex-col gap-space-md">
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant">
            <div className="flex flex-col md:flex-row gap-space-md items-start md:items-center">
              {preview && (
                <div className="w-full md:w-1/3 aspect-square rounded-lg overflow-hidden bg-surface-container shadow-inner flex-shrink-0">
                  <img src={preview} alt="Scanned Leaf" className="w-full h-full object-cover" />
                </div>
              )}
              
              <div className="flex-1 flex flex-col">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-3 py-1 rounded-full font-label-sm flex items-center gap-1 ${isHealthy ? 'bg-[#DCFCE7] text-[#166534] border border-[#86EFAC]' : 'bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]'}`}>
                    <span className="material-symbols-outlined text-[16px]">{isHealthy ? 'check_circle' : 'warning'}</span>
                    {isHealthy ? 'Healthy / Optimal' : 'Pathogen Detected'}
                  </span>
                  <span className="px-3 py-1 bg-surface-container text-on-surface-variant rounded-full font-label-sm">
                    {crop}
                  </span>
                </div>
                
                <h1 className="font-headline-lg text-primary mt-2">{result.class_label.replace(/___/g, ' - ').replace(/_/g, ' ')}</h1>
                
                <div className="mt-space-md bg-surface-container-low p-space-md rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-label-md text-on-surface">AI Confidence</span>
                    <span className="font-headline-sm text-primary">{confidencePercent}%</span>
                  </div>
                  <div className="w-full h-4 bg-surface-container-highest rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${isHealthy ? 'bg-secondary' : 'bg-tertiary'} rounded-full transition-all duration-1000 ease-out`} 
                      style={{ width: `${confidencePercent}%` }}
                    ></div>
                  </div>
                  <p className="text-body-sm text-on-surface-variant mt-2 text-right">Calibrated Neural Prediction</p>
                </div>
              </div>
            </div>
          </div>

          {/* Actionable Precaution */}
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border-l-4 border-l-tertiary">
            <h2 className="font-headline-md text-primary mb-space-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-tertiary">medical_services</span>
              Prescribed Treatment
            </h2>
            <p className="font-body-lg text-on-surface-variant">
              {result.precaution}
            </p>
          </div>
        </div>

        {/* Right Column: Bonus Modules (Mocked for now) */}
        <div className="lg:col-span-4 flex flex-col gap-space-md">
          {/* TODO: verify once bonus-modules branch is merged - Wire real irrigation_advisor.py endpoint */}
          <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm">
            <h3 className="font-headline-sm text-primary flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-[#0ea5e9]">water_drop</span>
              Irrigation Tip
            </h3>
            <p className="font-body-md text-on-surface-variant">
              Maintain soil moisture between 60-70%. Avoid overhead watering to prevent fungal spread.
            </p>
          </div>

          {/* TODO: verify once bonus-modules branch is merged - Wire real weather module */}
          <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm">
            <h3 className="font-headline-sm text-primary flex items-center gap-2 mb-3">
              <span className="material-symbols-outlined text-[#f59e0b]">partly_cloudy_day</span>
              Weather Note
            </h3>
            <p className="font-body-md text-on-surface-variant">
              High humidity expected over the next 48 hours. Ensure adequate canopy airflow.
            </p>
          </div>

          {/* TODO: verify once bonus-modules branch is merged - Wire real farmer_assistant.py chat interface */}
          <div className="bg-primary-container rounded-xl p-space-md shadow-sm mt-4">
            <h3 className="font-headline-sm text-on-primary-container flex items-center gap-2 mb-2">
              <span className="material-symbols-outlined">smart_toy</span>
              Ask the Assistant
            </h3>
            <p className="font-body-sm text-on-primary-container mb-4">
              Have questions about this {result.class_label.replace(/___/g, ' ')} diagnosis?
            </p>
            <button className="w-full py-2 bg-on-primary-container text-primary-container rounded-lg font-label-md flex justify-center items-center gap-2 hover:opacity-90">
              <span className="material-symbols-outlined">chat</span>
              Chat with AI
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
