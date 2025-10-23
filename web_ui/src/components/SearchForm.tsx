import { useState } from 'react';
import { Search, RefreshCw } from 'lucide-react';

interface SearchFormProps {
  onSearch: (params: {
    name: string;
    company?: string;
    title?: string;
    location?: string;
  }) => void;
  isSearching: boolean;
  onNewSearch: () => void;
  hasResults: boolean;
}

export default function SearchForm({
  onSearch,
  isSearching,
  onNewSearch,
  hasResults,
}: SearchFormProps) {
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [title, setTitle] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSearch({
        name: name.trim(),
        company: company.trim() || undefined,
        title: title.trim() || undefined,
        location: location.trim() || undefined,
      });
    }
  };

  const handleReset = () => {
    setName('');
    setCompany('');
    setTitle('');
    setLocation('');
    onNewSearch();
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-slate-800 dark:text-white mb-6">
        Profile Search
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name Field - Required */}
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
          >
            Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., John Doe"
            required
            disabled={isSearching}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg
                     bg-white dark:bg-slate-700 text-slate-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Company Field */}
        <div>
          <label
            htmlFor="company"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
          >
            Company
          </label>
          <input
            type="text"
            id="company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g., Microsoft"
            disabled={isSearching}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg
                     bg-white dark:bg-slate-700 text-slate-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Title Field */}
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
          >
            Job Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Software Engineer"
            disabled={isSearching}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg
                     bg-white dark:bg-slate-700 text-slate-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Location Field */}
        <div>
          <label
            htmlFor="location"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
          >
            Location
          </label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., San Francisco, CA"
            disabled={isSearching}
            className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg
                     bg-white dark:bg-slate-700 text-slate-900 dark:text-white
                     focus:ring-2 focus:ring-primary-500 focus:border-transparent
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSearching || !name.trim()}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium
                   py-3 px-4 rounded-lg transition-colors duration-200
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
        >
          {isSearching ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Search Profile
            </>
          )}
        </button>

        {/* New Search Button */}
        {hasResults && (
          <button
            type="button"
            onClick={handleReset}
            disabled={isSearching}
            className="w-full bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600
                     text-slate-700 dark:text-slate-200 font-medium
                     py-2 px-4 rounded-lg transition-colors duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            New Search
          </button>
        )}
      </form>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Note:</strong> This tool searches LinkedIn profiles via Google and performs general web searches.
          Results are aggregated and enhanced with AI analysis.
        </p>
      </div>
    </div>
  );
}
