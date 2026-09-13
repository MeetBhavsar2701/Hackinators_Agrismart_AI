import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictImage } from '../api';

export default function Upload() {
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      const url = URL.createObjectURL(selected);
      setPreview(url);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please upload a leaf photo first.');
      return;
    }
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await predictImage(file);
      navigate('/result', { state: { result, crop: selectedCrop, preview } });
    } catch (err) {
      setError(err.message);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col w-full">
      {/* Sunlight / High Contrast Mode Quick Bar */}
      <div className="w-full bg-surface-container-high py-space-sm px-gutter md:px-margin-tablet lg:px-margin-desktop flex items-center justify-between">
        <div className="flex items-center gap-space-sm">
          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-secondary-container text-on-secondary-container">
            <span className="material-symbols-outlined text-[16px]">wb_sunny</span>
          </span>
          <span className="font-label-md text-label-md text-on-surface">Outdoor High-Contrast Visibility Active</span>
        </div>
        <div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm">
          <span className="material-symbols-outlined text-[16px] text-secondary">wifi</span>
          <span>AI Diagnostics Engine Online</span>
        </div>
      </div>

      <section className="max-w-7xl mx-auto w-full px-gutter md:px-margin-tablet lg:px-margin-desktop py-space-lg md:py-space-xl">
        {/* Header Block */}
        <div className="max-w-3xl mb-space-lg">
          <div className="inline-flex items-center gap-space-xs px-space-sm py-1 rounded-full bg-primary-fixed text-on-primary-fixed font-label-sm text-label-sm mb-space-sm">
            <span className="material-symbols-outlined text-[14px]">psychology</span>
            <span>Neural Plant Pathologist 4.2</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-primary tracking-tight">Upload a photo of the affected leaf</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant mt-space-xs">
            Take a clear, bright photo of the leaf or select from gallery. Good sunlight gives best accuracy.
          </p>
        </div>

        {error && (
          <div className="mb-space-md p-space-md bg-error-container text-on-error-container rounded-lg font-label-md">
            <span className="material-symbols-outlined align-middle mr-2">error</span>
            {error}
          </div>
        )}

        {/* 2-Column Responsive Diagnostic Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg lg:gap-gutter-desktop items-start">
          {/* Left Column: Upload / Scanner Zone & Sample Preview */}
          <div className="lg:col-span-7 flex flex-col gap-space-md">
            <input 
              type="file" 
              accept="image/*" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
            />
            
            <div 
              className="relative group cursor-pointer bg-surface-container-lowest rounded-xl p-space-md md:p-space-lg shadow-sm transition-all duration-200"
              onClick={() => !preview && fileInputRef.current.click()}
            >
              <div className="relative w-full rounded-lg bg-surface-container-low p-space-md md:p-space-lg flex flex-col items-center justify-center text-center overflow-hidden min-h-[300px]">
                
                {preview ? (
                  <div className="relative w-full aspect-[4/3] rounded-lg overflow-hidden bg-surface-container flex items-center justify-center shadow-inner">
                    <img className="w-full h-full object-cover" src={preview} alt="Selected leaf" />
                    <div className="absolute inset-0 bg-gradient-to-t from-primary/80 via-transparent to-primary/20 pointer-events-none flex flex-col justify-between p-space-md">
                      <div className="flex items-center justify-between pointer-events-auto">
                        <span className="bg-surface-container-lowest/90 backdrop-blur text-primary px-space-sm py-1 rounded-full font-label-sm text-label-sm flex items-center gap-1 shadow-sm">
                          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
                          Target Acquired: Foliage
                        </span>
                        <button 
                          onClick={(e) => { e.stopPropagation(); setPreview(null); setFile(null); }}
                          className="w-9 h-9 rounded-full bg-surface-container-lowest/90 hover:bg-surface-container-lowest text-error flex items-center justify-center shadow-sm transition-colors" 
                          type="button"
                        >
                          <span className="material-symbols-outlined text-[20px]">close</span>
                        </button>
                      </div>
                      <div className="mx-auto w-48 h-48 rounded-lg flex items-center justify-center relative shadow-sm border border-secondary-container/50">
                         <span className="text-on-primary font-label-sm text-label-sm bg-primary/80 px-2 py-0.5 rounded shadow absolute -bottom-3">Foliar Lesions Detected</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <span className="material-symbols-outlined text-[48px] text-primary">add_photo_alternate</span>
                    <span className="font-headline-sm text-primary">Tap to select or take photo</span>
                  </div>
                )}
                
                <div className="mt-space-md flex flex-wrap items-center justify-center gap-space-sm text-on-surface-variant font-label-md text-label-md">
                  {preview && (
                    <>
                      <span className="inline-flex items-center gap-1 text-secondary font-label-lg text-label-lg">
                        <span className="material-symbols-outlined text-[20px]">check_circle</span> Ready for AI Inference
                      </span>
                      <span>•</span>
                    </>
                  )}
                  <span>JPG, PNG, HEIC up to 25MB</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-md">
              <button 
                onClick={() => fileInputRef.current.click()}
                className="min-h-[56px] px-space-md py-space-sm bg-surface-container-lowest hover:bg-surface-container rounded-xl shadow-sm flex items-center justify-center gap-space-sm active:translate-y-0.5 transition-all text-primary font-label-lg text-label-lg group" 
                type="button"
              >
                <span className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-on-primary-fixed transition-transform group-hover:scale-110">
                  <span className="material-symbols-outlined text-[24px]">photo_camera</span>
                </span>
                <div className="text-left">
                  <div className="font-label-lg text-label-lg text-primary">Take Photo</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Live field camera</div>
                </div>
              </button>
              <button 
                onClick={() => fileInputRef.current.click()}
                className="min-h-[56px] px-space-md py-space-sm bg-surface-container-lowest hover:bg-surface-container rounded-xl shadow-sm flex items-center justify-center gap-space-sm active:translate-y-0.5 transition-all text-primary font-label-lg text-label-lg group" 
                type="button"
              >
                <span className="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center text-on-secondary-container transition-transform group-hover:scale-110">
                  <span className="material-symbols-outlined text-[24px]">collections</span>
                </span>
                <div className="text-left">
                  <div className="font-label-lg text-label-lg text-primary">Choose Gallery</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant">Select saved image</div>
                </div>
              </button>
            </div>
          </div>

          {/* Right Column */}
          <div className="lg:col-span-5 flex flex-col gap-space-md">
            <div className="bg-surface-container-lowest rounded-xl p-space-md md:p-space-lg shadow-sm">
              <div className="flex items-center justify-between mb-space-sm">
                <label className="font-label-lg text-label-lg text-on-surface flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[20px] text-secondary">potted_plant</span>
                  Select Crop Species
                </label>
                <span className="font-label-sm text-label-sm text-on-surface-variant bg-surface-container px-2 py-0.5 rounded">Required</span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mb-space-md">
                Calibrates algorithmic neural weights to target specific host pathology.
              </p>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-space-xs md:gap-space-sm">
                {['Tomato', 'Potato', 'Apple', 'Corn', 'Cherry', 'Grape'].map(crop => (
                  <button 
                    key={crop}
                    onClick={() => setSelectedCrop(crop)}
                    className={`min-h-[48px] px-space-sm py-2 rounded-lg font-label-md text-label-md flex items-center justify-between transition-all ${
                      selectedCrop === crop 
                        ? 'bg-primary-container text-on-primary shadow-sm' 
                        : 'bg-surface-container-low hover:bg-surface-container text-on-surface'
                    }`}
                  >
                    <span>{crop}</span>
                    <span className={`material-symbols-outlined text-[18px] ${selectedCrop === crop ? 'text-secondary-fixed' : 'opacity-0'}`}>check</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-surface-container-lowest rounded-xl p-space-md shadow-sm">
              <div className="font-label-md text-label-md text-on-surface mb-space-sm flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px] text-secondary">thermostat</span>
                  Field Conditions Log
                </span>
                <span className="text-on-secondary-container bg-secondary-container px-2 py-0.5 rounded-full font-label-sm text-label-sm">Station Alpha-4</span>
              </div>
              <div className="grid grid-cols-2 gap-space-sm">
                <div className="p-space-sm rounded-lg bg-surface-container-low">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">Canopy Humidity</span>
                  <div className="font-headline-sm text-headline-sm text-primary mt-1">78%</div>
                  <span className="font-label-sm text-label-sm text-tertiary">Elevated Fungal Risk</span>
                </div>
                <div className="p-space-sm rounded-lg bg-surface-container-low">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">Ambient Temp</span>
                  <div className="font-headline-sm text-headline-sm text-primary mt-1">27.4°C</div>
                  <span className="font-label-sm text-label-sm text-secondary">Optimal Growth</span>
                </div>
              </div>
            </div>

            <div className="mt-space-xs flex flex-col gap-space-xs">
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing || !preview}
                className={`w-full min-h-[64px] rounded-xl font-headline-sm text-headline-sm shadow-md flex items-center justify-center gap-space-sm transition-all ${
                  isAnalyzing || !preview 
                    ? 'bg-surface-container text-on-surface-variant cursor-not-allowed' 
                    : 'bg-primary-container hover:bg-primary text-on-primary active:translate-y-1'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <span className="material-symbols-outlined text-[28px] animate-spin">progress_activity</span>
                    <span>Running Pathogen Matcher...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[28px] text-secondary-fixed">search_insights</span>
                    <span>Analyze Plant Health</span>
                  </>
                )}
              </button>
              <div className="flex items-center justify-center gap-2 text-on-surface-variant font-label-sm text-label-sm py-1">
                <span className="material-symbols-outlined text-[16px] text-secondary">verified_user</span>
                <span>Offline-first model caching active. 100% private data.</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
