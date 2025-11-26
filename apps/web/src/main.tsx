import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { store } from './store/store'
import App from './App'
import './index.css'
import './i18n/config'
import { SidebarProvider } from '@/contexts/SidebarContext'
import { SidebarThemeProvider } from '@/contexts/SidebarThemeContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <SidebarProvider>
          <SidebarThemeProvider>
            <App />
            <Toaster position="top-right" />
          </SidebarThemeProvider>
        </SidebarProvider>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)
