import { useState } from 'react';
import { FileText, ExternalLink, Download, Linkedin, Globe, Newspaper } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface SearchResponse {
  success: boolean;
  search_id: string;
  session_id: string;
  data: any;
  report: string;
  timestamp: string;
}

interface ReportDisplayProps {
  report: SearchResponse;
}

export default function ReportDisplay({ report }: ReportDisplayProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'linkedin' | 'web' | 'news' | 'full'>(
    'summary'
  );

  const { data } = report;
  const summary = data?.summary || {};
  const linkedin = data?.linkedin || {};
  const web = data?.web_search || {};
  const news = data?.news || {};

  const downloadReport = () => {
    const blob = new Blob([report.report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `profile-report-${report.search_id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <FileText className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-semibold text-slate-800 dark:text-white">Report</h2>
        </div>
        <button
          onClick={downloadReport}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-100 hover:bg-slate-200
                   dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200
                   rounded-lg transition-colors"
        >
          <Download className="w-4 h-4" />
          Download
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
        <button
          onClick={() => setActiveTab('summary')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'summary'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
        >
          <FileText className="w-4 h-4" />
          Summary
        </button>
        <button
          onClick={() => setActiveTab('linkedin')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'linkedin'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
        >
          <Linkedin className="w-4 h-4" />
          LinkedIn ({linkedin.count || 0})
        </button>
        <button
          onClick={() => setActiveTab('web')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'web'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
        >
          <Globe className="w-4 h-4" />
          Web ({web.count || 0})
        </button>
        <button
          onClick={() => setActiveTab('news')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'news'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
        >
          <Newspaper className="w-4 h-4" />
          News ({news.count || 0})
        </button>
        <button
          onClick={() => setActiveTab('full')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'full'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
        >
          Full Report
        </button>
      </div>

      {/* Content */}
      <div className="p-6 overflow-y-auto max-h-[calc(100vh-20rem)]">
        {activeTab === 'summary' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <p className="text-sm text-slate-600 dark:text-slate-400">Total Results</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-white">
                  {summary.total_results || 0}
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <p className="text-sm text-slate-600 dark:text-slate-400">Data Sources</p>
                <p className="text-2xl font-bold text-slate-800 dark:text-white">
                  {[summary.has_linkedin_profile, summary.has_web_presence, summary.has_news_coverage].filter(Boolean).length}
                </p>
              </div>
            </div>

            {summary.top_linkedin_profile && (
              <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                <h3 className="font-semibold text-slate-800 dark:text-white mb-2 flex items-center gap-2">
                  <Linkedin className="w-5 h-5 text-blue-600" />
                  Top LinkedIn Profile
                </h3>
                <p className="text-slate-700 dark:text-slate-300 mb-2">
                  {summary.top_linkedin_profile.title}
                </p>
                <a
                  href={summary.top_linkedin_profile.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary-600 hover:underline flex items-center gap-1"
                >
                  View Profile <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>
        )}

        {activeTab === 'linkedin' && (
          <div className="space-y-4">
            {linkedin.profiles && linkedin.profiles.length > 0 ? (
              linkedin.profiles.map((profile: any, index: number) => (
                <div
                  key={index}
                  className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <h3 className="font-semibold text-slate-800 dark:text-white mb-2">
                    {profile.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                    {profile.snippet}
                  </p>
                  <a
                    href={profile.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-600 hover:underline flex items-center gap-1"
                  >
                    Open in LinkedIn <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))
            ) : (
              <p className="text-slate-500 dark:text-slate-400 text-center py-8">
                No LinkedIn profiles found
              </p>
            )}
          </div>
        )}

        {activeTab === 'web' && (
          <div className="space-y-4">
            {web.results && web.results.length > 0 ? (
              web.results.map((result: any, index: number) => (
                <div
                  key={index}
                  className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <h3 className="font-semibold text-slate-800 dark:text-white mb-2">
                    {result.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                    {result.snippet}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mb-3">
                    {result.display_url}
                  </p>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-600 hover:underline flex items-center gap-1"
                  >
                    Visit Website <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))
            ) : (
              <p className="text-slate-500 dark:text-slate-400 text-center py-8">
                No web results found
              </p>
            )}
          </div>
        )}

        {activeTab === 'news' && (
          <div className="space-y-4">
            {news.articles && news.articles.length > 0 ? (
              news.articles.map((article: any, index: number) => (
                <div
                  key={index}
                  className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-slate-800 dark:text-white flex-1">
                      {article.title}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-500 mb-2">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>{article.date}</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                    {article.snippet}
                  </p>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-600 hover:underline flex items-center gap-1"
                  >
                    Read Article <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))
            ) : (
              <p className="text-slate-500 dark:text-slate-400 text-center py-8">
                No news articles found
              </p>
            )}
          </div>
        )}

        {activeTab === 'full' && (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{report.report}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
