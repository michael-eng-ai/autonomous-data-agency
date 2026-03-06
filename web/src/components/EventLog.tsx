import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  Terminal,
  Clock,
  Search,
  Filter,
  Download,
  X
} from 'lucide-react';

interface LogEvent {
  type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

interface EventLogProps {
  events: LogEvent[];
}

type EventCategory = 'all' | 'team' | 'project' | 'error';

export const EventLog: React.FC<EventLogProps> = ({ events }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<LogEvent | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<EventCategory>('all');
  const [showFilters, setShowFilters] = useState(false);

  const getEventIcon = (type: string) => {
    if (type.includes('completed')) return '✅';
    if (type.includes('started')) return '🚀';
    if (type.includes('error')) return '❌';
    if (type.includes('phase')) return '📊';
    if (type.includes('message')) return '💬';
    if (type.includes('dialog')) return '💭';
    return '📌';
  };

  const getEventColor = (type: string) => {
    if (type.includes('completed')) return 'text-green-400';
    if (type.includes('started')) return 'text-blue-400';
    if (type.includes('error')) return 'text-red-400';
    if (type.includes('phase')) return 'text-purple-400';
    if (type.includes('dialog')) return 'text-cyan-400';
    return 'text-gray-400';
  };

  const formatEventType = (type: string) => {
    return type
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, c => c.toUpperCase());
  };

  const getEventCategory = (type: string): EventCategory => {
    if (type.includes('error')) return 'error';
    if (type.includes('team')) return 'team';
    if (type.includes('project') || type.includes('phase')) return 'project';
    return 'all';
  };

  // Filtra eventos
  const filteredEvents = useMemo(() => {
    return events.filter(evt => {
      // Filtro por categoria
      if (filterCategory !== 'all') {
        const category = getEventCategory(evt.type);
        if (category !== filterCategory && category !== 'all') {
          return false;
        }
      }

      // Filtro por busca
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const typeMatch = evt.type.toLowerCase().includes(query);
        const dataMatch = JSON.stringify(evt.data).toLowerCase().includes(query);
        return typeMatch || dataMatch;
      }

      return true;
    });
  }, [events, filterCategory, searchQuery]);

  const displayedEvents = isExpanded ? filteredEvents : filteredEvents.slice(0, 5);

  const handleExport = () => {
    const dataStr = JSON.stringify(events, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `event-log-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const categoryOptions: { value: EventCategory; label: string; color: string }[] = [
    { value: 'all', label: 'Todos', color: 'text-gray-400' },
    { value: 'team', label: 'Times', color: 'text-blue-400' },
    { value: 'project', label: 'Projeto', color: 'text-purple-400' },
    { value: 'error', label: 'Erros', color: 'text-red-400' }
  ];

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2"
          >
            <Terminal className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-300">Log de Eventos</span>
            <span className="text-xs bg-gray-700 px-2 py-0.5 rounded-full text-gray-400">
              {filteredEvents.length}
              {filteredEvents.length !== events.length && (
                <span className="text-gray-500">/{events.length}</span>
              )}
            </span>
          </button>

          <div className="flex items-center gap-2">
            {/* Botão de filtro */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-1.5 rounded-lg transition-colors ${
                showFilters || filterCategory !== 'all' || searchQuery
                  ? 'bg-blue-500/20 text-blue-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
              title="Filtros"
            >
              <Filter className="w-4 h-4" />
            </button>

            {/* Botão de exportar */}
            <button
              onClick={handleExport}
              className="p-1.5 text-gray-500 hover:text-gray-300 rounded-lg transition-colors"
              title="Exportar eventos"
            >
              <Download className="w-4 h-4" />
            </button>

            {/* Botão expandir */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1.5 text-gray-500 hover:text-gray-300 transition-colors"
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Filtros */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="pt-3 space-y-2">
                {/* Busca */}
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Buscar eventos..."
                    className="w-full pl-8 pr-8 py-1.5 text-xs bg-gray-900/50 border border-gray-700 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-300"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>

                {/* Categorias */}
                <div className="flex gap-1">
                  {categoryOptions.map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setFilterCategory(opt.value)}
                      className={`px-2 py-1 text-xs rounded-lg transition-colors ${
                        filterCategory === opt.value
                          ? `${opt.color} bg-gray-700`
                          : 'text-gray-500 hover:text-gray-300 hover:bg-gray-700/50'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Event List */}
      <div className={`transition-all duration-300 ${isExpanded ? 'max-h-80' : 'max-h-48'} overflow-y-auto custom-scrollbar`}>
        {filteredEvents.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            {events.length === 0
              ? 'Nenhum evento registrado ainda...'
              : 'Nenhum evento encontrado com os filtros atuais.'}
          </div>
        ) : (
          <div className="divide-y divide-gray-700/50">
            <AnimatePresence initial={false}>
              {displayedEvents.map((evt, idx) => {
                const teamName = evt.data?.team ? String(evt.data.team).replace(/_/g, ' ') : null;
                const summary = evt.data?.summary ? String(evt.data.summary) : null;

                return (
                  <motion.div
                    key={`${evt.type}-${evt.timestamp}-${idx}`}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: idx * 0.02 }}
                    onClick={() => setSelectedEvent(selectedEvent === evt ? null : evt)}
                    className="p-3 hover:bg-gray-700/30 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{getEventIcon(evt.type)}</span>
                      <span className={`text-sm font-medium ${getEventColor(evt.type)}`}>
                        {formatEventType(evt.type)}
                      </span>

                      {/* Team badge */}
                      {teamName && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">
                          {teamName}
                        </span>
                      )}

                      <span className="ml-auto text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(evt.timestamp).toLocaleTimeString('pt-BR')}
                      </span>
                    </div>

                    {/* Expanded details */}
                    {selectedEvent === evt && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs font-mono text-gray-400 overflow-x-auto">
                          <pre className="whitespace-pre-wrap">
                            {JSON.stringify(evt.data, null, 2)}
                          </pre>
                        </div>
                      </motion.div>
                    )}

                    {/* Summary preview */}
                    {summary && selectedEvent !== evt && (
                      <div className="mt-1 text-xs text-gray-500 truncate pl-6">
                        {summary.substring(0, 80)}...
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Show more button */}
      {filteredEvents.length > 5 && !isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full p-2 text-xs text-blue-400 hover:text-blue-300 hover:bg-gray-700/30 transition-colors border-t border-gray-700"
        >
          Ver mais {filteredEvents.length - 5} eventos...
        </button>
      )}
    </div>
  );
};
