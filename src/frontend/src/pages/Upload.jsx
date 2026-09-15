import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictImage } from '../api';

const CROPS = ['Tomato', 'Potato', 'Apple', 'Corn', 'Grape', 'Bell pepper'];
const ACCEPTED = 'image/png,image/jpeg,image/webp';

export default function Upload() {
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null); // null = checking
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // Real readiness check against the backend. No hardcoded "online" claim.
  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setHealth)
      .catch(() => setHealth(false));
  }, []);

  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return setError('Select a leaf photo first.');
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

  const clearImage = (e) => {
    e.stopPropagation();
    setPreview(null);
    setFile(null);
    setError(null);
  };

  return (
    <section className="max-w-6xl mx-auto w-full px-gutter md:px-margin-tablet lg:px-margin-desktop py-space-lg md:py-space-xl">
      {/* Title + real model identity */}
      <header className="mb-space-lg">
        <div className="flex flex-wrap items-center gap-space-xs mb-space-sm">
          <span className="inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-surface-container text-on-surface-variant font-label-sm text-label-sm">
            <span className="material-symbols-outlined text-[14px]">neurology</span>
            EfficientNet-B0
            {health && health.num_classes ? ` · ${health.num_classes} classes` : ''}
          </span>
          <span
            className={`inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full font-label-sm text-label-sm ${
              health === null
                ? 'bg-surface-container text-on-surface-variant'
                : health
                  ? 'bg-secondary-container text-on-secondary-container'
                  : 'bg-error-container text-on-error-container'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                health === null ? 'bg-on-surface-variant' : health ? 'bg-secondary' : 'bg-error'
              }`}
            />
            {health === null ? 'Checking backend…' : health ? 'Backend connected' : 'Backend offline'}
          </span>
        </div>

        <h1 className="font-headline-lg text-headline-lg text-primary tracking-tight">
          Upload a photo of the affected leaf
        </h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant mt-space-xs max-w-2xl">
          One leaf, filling most of the frame, in daylight. Avoid shadows and blur.
        </p>
      </header>

      {error && (
        <div
          role="alert"
          className="mb-space-md p-space-md bg-error-container text-on-error-container rounded-xl font-label-md flex items-start gap-space-sm"
        >
          <span className="material-symbols-outlined text-[20px]">error</span>
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        {/* Upload zone */}
        <div className="lg:col-span-7 flex flex-col gap-space-md">
          <input
            type="file"
            accept={ACCEPTED}
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileChange}
          />

          {preview ? (
            <figure className="relative rounded-xl overflow-hidden bg-surface-container border border-outline-variant">
              <img src={preview} alt="Selected leaf" className="w-full aspect-[4/3] object-cover" />
              <button
                type="button"
                onClick={clearImage}
                aria-label="Remove image"
                className="absolute top-3 right-3 w-9 h-9 rounded-full bg-surface-container-lowest/95 text-error flex items-center justify-center shadow-sm hover:bg-surface-container-lowest transition-colors"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
              <figcaption className="px-space-md py-space-sm font-body-sm text-body-sm text-on-surface-variant border-t border-outline-variant truncate">
                {file?.name}
              </figcaption>
            </figure>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current.click()}
              className="w-full min-h-[320px] rounded-xl border-2 border-dashed border-outline-variant bg-surface-container-lowest hover:border-primary hover:bg-surface-container-low transition-colors flex flex-col items-center justify-center gap-space-sm text-center px-space-md"
            >
              <span className="material-symbols-outlined text-[44px] text-primary">add_photo_alternate</span>
              <span className="font-headline-sm text-primary">Select or take a photo</span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">JPG, PNG or WebP</span>
            </button>
          )}

          <div className="grid grid-cols-2 gap-space-md">
            <button
              type="button"
              onClick={() => fileInputRef.current.click()}
              className="min-h-[56px] px-space-md rounded-xl bg-surface-container-lowest border border-outline-variant hover:bg-surface-container transition-colors flex items-center justify-center gap-space-sm text-primary font-label-lg text-label-lg"
            >
              <span className="material-symbols-outlined text-[22px]">photo_camera</span>
              Take photo
            </button>
            <button
              type="button"
              onClick={() => fileInputRef.current.click()}
              className="min-h-[56px] px-space-md rounded-xl bg-surface-container-lowest border border-outline-variant hover:bg-surface-container transition-colors flex items-center justify-center gap-space-sm text-primary font-label-lg text-label-lg"
            >
              <span className="material-symbols-outlined text-[22px]">collections</span>
              Choose file
            </button>
          </div>
        </div>

        {/* Context + action */}
        <aside className="lg:col-span-5 flex flex-col gap-space-md">
          <div className="bg-surface-container-lowest rounded-xl p-space-md md:p-space-lg border border-outline-variant">
            <label className="font-label-lg text-label-lg text-on-surface flex items-center gap-1.5 mb-space-xs">
              <span className="material-symbols-outlined text-[20px] text-secondary">potted_plant</span>
              Crop
            </label>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-space-md">
              Recorded alongside your scan for context. The model reads the image only — it does not
              filter by crop.
            </p>

            <div className="grid grid-cols-2 gap-space-xs">
              {CROPS.map((crop) => (
                <button
                  key={crop}
                  type="button"
                  onClick={() => setSelectedCrop(crop)}
                  aria-pressed={selectedCrop === crop}
                  className={`min-h-[44px] px-space-sm rounded-lg font-label-md text-label-md text-left transition-colors ${
                    selectedCrop === crop
                      ? 'bg-primary text-on-primary'
                      : 'bg-surface-container-low hover:bg-surface-container text-on-surface'
                  }`}
                >
                  {crop}
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={isAnalyzing || !preview}
            className={`w-full min-h-[60px] rounded-xl font-headline-sm text-headline-sm shadow-sm flex items-center justify-center gap-space-sm transition-all ${
              isAnalyzing || !preview
                ? 'bg-surface-container text-on-surface-variant cursor-not-allowed'
                : 'bg-primary hover:opacity-90 text-on-primary active:translate-y-0.5'
            }`}
          >
            {isAnalyzing ? (
              <>
                <span className="material-symbols-outlined text-[26px] animate-spin">progress_activity</span>
                Analysing…
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[26px]">search_insights</span>
                Analyse leaf
              </>
            )}
          </button>

          {/* Honest capability disclosure */}
          <div className="rounded-xl p-space-md bg-surface-container-low border border-outline-variant">
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              <span className="material-symbols-outlined text-[16px] align-middle mr-1 text-tertiary">
                info
              </span>
              <strong className="text-on-surface">Research prototype.</strong> Accuracy on real field
              photos is currently low (macro-F1 0.069). Treat any result as a prompt to inspect the
              crop, not a diagnosis. For advice you can act on, call the Kisan Call Centre on{' '}
              <a href="tel:18001801551" className="text-primary underline">
                1800-180-1551
              </a>
              .
            </p>
          </div>

          <p className="font-label-sm text-label-sm text-on-surface-variant text-center">
            Images are sent to the API running on this machine. Nothing is uploaded elsewhere.
          </p>
        </aside>
      </div>
    </section>
  );
}
