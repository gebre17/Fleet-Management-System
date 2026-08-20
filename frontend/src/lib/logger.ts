/**
 * Lightweight structured client logger.
 *
 * Wraps console methods with a consistent { level, context, message, ... }
 * shape instead of ad-hoc strings, so frontend errors are easy to grep or
 * feed into a log aggregator later without changing every call site again.
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogMeta {
  [key: string]: unknown;
}

export interface LogEntry {
  level: LogLevel;
  context: string;
  message: string;
  timestamp: string;
  meta?: LogMeta;
}

function emit(level: LogLevel, context: string, message: string, meta?: LogMeta): LogEntry {
  const entry: LogEntry = {
    level,
    context,
    message,
    timestamp: new Date().toISOString(),
    ...(meta ? { meta } : {}),
  };

  // Looked up on `console` at call time (not captured at module load) so
  // test spies like `jest.spyOn(console, 'error')` actually intercept this.
  console[level](entry);
  return entry;
}

export const logger = {
  debug: (context: string, message: string, meta?: LogMeta) => emit('debug', context, message, meta),
  info: (context: string, message: string, meta?: LogMeta) => emit('info', context, message, meta),
  warn: (context: string, message: string, meta?: LogMeta) => emit('warn', context, message, meta),
  error: (context: string, message: string, meta?: LogMeta) => emit('error', context, message, meta),
};
