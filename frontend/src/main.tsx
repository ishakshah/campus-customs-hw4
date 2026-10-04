import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import AuthProvider from './AuthProvider.tsx'
import ResultsProvider from './ResultsProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ResultsProvider>
          <App />
        </ResultsProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
