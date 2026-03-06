import { useState } from 'react';
import { Smile, Flame, Zap, Users, ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';

interface PersonalitySelectionProps {
  onBack: () => void;
  onNext: (personality: string) => void;
}

interface Personality {
  id: string;
  name: string;
  icon: typeof Smile;
  color: string;
  bgColor: string;
  borderColor: string;
  description: string;
  traits: string[];
}

export default function PersonalitySelection({ onBack, onNext }: PersonalitySelectionProps) {
  const [selectedPersonality, setSelectedPersonality] = useState<string>('');

  const personalities: Personality[] = [
    {
      id: 'friendly',
      name: 'Friendly HR',
      icon: Smile,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-500',
      description: 'A warm and approachable interviewer focused on getting to know you',
      traits: ['Encouraging', 'Patient', 'Conversational', 'Supportive']
    },
    {
      id: 'technical',
      name: 'Strict Technical',
      icon: Flame,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-500',
      description: 'A rigorous technical expert who tests your knowledge in-depth',
      traits: ['Detail-oriented', 'Challenging', 'Precise', 'Expert-level']
    },
    {
      id: 'stress',
      name: 'Stress Interview',
      icon: Zap,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-500',
      description: 'A high-pressure interviewer who tests your composure under stress',
      traits: ['Fast-paced', 'Probing', 'Intense', 'Challenging']
    },
    {
      id: 'panel',
      name: 'Panel Interview',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      description: 'Multiple interviewers with different perspectives and questions',
      traits: ['Multi-faceted', 'Diverse', 'Comprehensive', 'Professional']
    }
  ];

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Resume Upload
        </button>

        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 border border-slate-200">
          <div className="mb-12 text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-3">
              Choose Your Interviewer
            </h1>
            <p className="text-slate-600 text-lg max-w-2xl mx-auto">
              Select the interviewer personality that matches your target interview style. Each type
              offers a unique preparation experience.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {personalities.map((personality) => {
              const Icon = personality.icon;
              const isSelected = selectedPersonality === personality.id;

              return (
                <button
                  key={personality.id}
                  onClick={() => setSelectedPersonality(personality.id)}
                  className={`text-left p-6 rounded-xl border-3 transition-all transform hover:scale-105 ${
                    isSelected
                      ? `${personality.borderColor} ${personality.bgColor} shadow-lg`
                      : 'border-slate-200 bg-white hover:border-slate-300 shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-14 h-14 rounded-lg flex items-center justify-center ${personality.bgColor}`}>
                      <Icon className={`w-7 h-7 ${personality.color}`} />
                    </div>
                    {isSelected && (
                      <CheckCircle className={`w-7 h-7 ${personality.color}`} />
                    )}
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 mb-2">
                    {personality.name}
                  </h3>

                  <p className="text-slate-600 mb-4 leading-relaxed">
                    {personality.description}
                  </p>

                  <div className="flex flex-wrap gap-2">
                    {personality.traits.map((trait, index) => (
                      <span
                        key={index}
                        className={`text-sm px-3 py-1 rounded-full ${
                          isSelected
                            ? `${personality.bgColor} ${personality.color} font-medium`
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {trait}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })}
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => selectedPersonality && onNext(selectedPersonality)}
              disabled={!selectedPersonality}
              className={`flex items-center gap-2 px-8 py-3 rounded-lg font-semibold transition-all ${
                selectedPersonality
                  ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg'
                  : 'bg-slate-300 text-slate-500 cursor-not-allowed'
              }`}
            >
              Start Interview
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex gap-3">
            <Users className="w-6 h-6 text-blue-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Practice Makes Perfect</h3>
              <p className="text-slate-700 text-sm leading-relaxed">
                Each personality type prepares you for different real-world scenarios. We recommend
                practicing with multiple types to build comprehensive interview skills and adaptability.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
