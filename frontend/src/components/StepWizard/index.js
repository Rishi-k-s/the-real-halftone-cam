import React from 'react';
import { Camera, Settings, Printer, Image } from 'lucide-react';

const StepWizard = ({ currentStep, onStepChange, canProceed }) => {
  const steps = [
    { id: 1, name: 'Capture', icon: Camera, description: 'Take a photo' },
    { id: 2, name: 'Process', icon: Settings, description: 'Apply effects' },
    { id: 3, name: 'Print', icon: Printer, description: 'Print image' },
    { id: 4, name: 'Gallery', icon: Image, description: 'View history' },
  ];

  const handleStepClick = (stepId) => {
    // Enforce flow: can only go to next step if current step is complete
    if (stepId <= currentStep + (canProceed ? 1 : 0)) {
      onStepChange(stepId);
    }
  };

  return (
    <div className="w-full bg-white shadow-sm border-b">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <nav aria-label="Progress">
          <ol className="flex items-center justify-between">
            {steps.map((step, stepIdx) => {
              const isCompleted = step.id < currentStep;
              const isCurrent = step.id === currentStep;
              const isAccessible = step.id <= currentStep + (canProceed ? 1 : 0);

              return (
                <li key={step.id} className="flex items-center">
                  <button
                    onClick={() => handleStepClick(step.id)}
                    disabled={!isAccessible}
                    className={`
                      group flex flex-col items-center px-2 py-2 text-sm font-medium rounded-lg transition-all
                      ${isAccessible ? 'cursor-pointer hover:bg-gray-50' : 'cursor-not-allowed opacity-50'}
                      ${isCurrent ? 'text-primary-600' : ''}
                      ${isCompleted ? 'text-green-600' : ''}
                    `}
                  >
                    <span
                      className={`
                        flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all
                        ${isCurrent ? 'border-primary-600 bg-primary-600 text-white' : ''}
                        ${isCompleted ? 'border-green-600 bg-green-600 text-white' : ''}
                        ${!isCurrent && !isCompleted && isAccessible ? 'border-gray-300 text-gray-500 group-hover:border-gray-400' : ''}
                        ${!isAccessible ? 'border-gray-200 text-gray-300' : ''}
                      `}
                    >
                      <step.icon className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <span className="mt-1 text-xs">{step.name}</span>
                  </button>

                  {stepIdx < steps.length - 1 && (
                    <div
                      className={`
                        hidden sm:block h-0.5 w-16 mx-2 transition-colors
                        ${isCompleted ? 'bg-green-600' : 'bg-gray-200'}
                      `}
                    />
                  )}
                </li>
              );
            })}
          </ol>
        </nav>
      </div>
    </div>
  );
};

export default StepWizard;
