import { useState, useEffect } from 'react';
import Head from 'next/head';
import SearchForm from '@/components/SearchForm';
import ChatInterface from '@/components/ChatInterface';
import ReportDisplay from '@/components/ReportDisplay';
import { searchProfile, sendChatMessage, SearchResponse, ChatResponse } from '@/lib/api';

export default function Home() {
  const [sessionId, setSessionId] = useState<string>('');
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    sources?: any[];
  }>>([]);

  useEffect(() => {
    // Generate session ID on mount
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  const handleSearch = async (searchParams: {
    name: string;
    company?: string;
    title?: string;
    location?: string;
  }) => {
    setIsSearching(true);
    try {
      const result = await searchProfile({
        ...searchParams,
        session_id: sessionId,
      });

      setSearchResult(result);

      // Add system message about search completion
      setChatMessages([
        {
          role: 'assistant',
          content: `I've found information about **${searchParams.name}**. The search returned ${result.data.summary.total_results} results across LinkedIn, web search, and news. You can ask me any questions about the findings!`,
          timestamp: result.timestamp,
        },
      ]);
    } catch (error: any) {
      console.error('Search error:', error);
      setChatMessages([
        {
          role: 'assistant',
          content: `Sorry, I encountered an error while searching: ${error.message || 'Unknown error'}. Please check your API keys and try again.`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleChatMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage = {
      role: 'user' as const,
      content: message,
      timestamp: new Date().toISOString(),
    };
    setChatMessages((prev) => [...prev, userMessage]);

    try {
      // Send to API
      const response: ChatResponse = await sendChatMessage({
        session_id: sessionId,
        message: message,
        search_id: searchResult?.search_id,
      });

      // Add assistant response
      const assistantMessage = {
        role: 'assistant' as const,
        content: response.message,
        timestamp: response.timestamp,
        sources: response.sources,
      };
      setChatMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setChatMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleNewSearch = () => {
    setSearchResult(null);
    setChatMessages([]);
  };

  return (
    <>
      <Head>
        <title>Profile Search - LinkedIn & Web Intelligence</title>
        <meta name="description" content="Search and analyze professional profiles with AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-slate-800 dark:text-white mb-2">
              Profile Search Intelligence
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-300">
              AI-powered LinkedIn and web profile analysis
            </p>
          </header>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Search Form */}
            <div className="lg:col-span-1">
              <SearchForm
                onSearch={handleSearch}
                isSearching={isSearching}
                onNewSearch={handleNewSearch}
                hasResults={!!searchResult}
              />
            </div>

            {/* Middle Column - Report Display */}
            <div className="lg:col-span-1">
              {searchResult ? (
                <ReportDisplay report={searchResult} />
              ) : (
                <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8 text-center">
                  <div className="text-slate-400 dark:text-slate-500">
                    <svg
                      className="mx-auto h-24 w-24 mb-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                    <p className="text-lg">Start a search to see results</p>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Chat Interface */}
            <div className="lg:col-span-1">
              <ChatInterface
                messages={chatMessages}
                onSendMessage={handleChatMessage}
                disabled={!searchResult && !isSearching}
              />
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-12 text-center text-sm text-slate-500 dark:text-slate-400">
            <p>
              Built with Next.js, FastAPI, and OpenAI | Respects privacy and ethical use
            </p>
          </footer>
        </div>
      </main>
    </>
  );
}
