import { createContext, useContext } from 'react'
import type { SearchResults } from './types'

export interface ResultsState {
  /** Search results from the Personal Assistant that the Products page is currently showing, if any. */
  results: SearchResults | null
  showResults: (results: SearchResults) => void
  clearResults: () => void
}

export const ResultsContext = createContext<ResultsState | null>(null)

export function useSearchResults(): ResultsState {
  const ctx = useContext(ResultsContext)
  if (!ctx) throw new Error('useSearchResults must be used inside <ResultsProvider>')
  return ctx
}
