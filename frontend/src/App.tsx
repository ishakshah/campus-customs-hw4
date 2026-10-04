import { Route, Routes } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ChatWidget from './components/ChatWidget'
import Footer from './components/Footer'
import NavBar from './components/NavBar'
import PasswordBanner from './components/PasswordBanner'
import About from './pages/About'
import CreateAccount from './pages/CreateAccount'
import Explore from './pages/Explore'
import Home from './pages/Home'
import Login from './pages/Login'
import ProductDetail from './pages/ProductDetail'
import Products from './pages/Products'
import UpdatePassword from './pages/UpdatePassword'

export default function App() {
  const { user } = useAuth()
  return (
    <div className="app">
      <NavBar />
      <PasswordBanner />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductDetail />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="/update-password" element={<UpdatePassword />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <Footer />
      <ChatWidget key={user?.id ?? 'guest'} />  {/* fresh conversation when someone logs in or out */}
    </div>
  )
}
