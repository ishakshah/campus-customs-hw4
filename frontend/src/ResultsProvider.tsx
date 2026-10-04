import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { ResultsContext } from './ResultsContext'
import type { SearchResults } from './types'

export default function ResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<SearchResults | null>(null)
  const value = useMemo(
    () => ({ results, showResults: setResults, clearResults: () => setResults(null) }),
    [results],
  )
  return <ResultsContext.Provider value={value}>{children}</ResultsContext.Provider>
}
