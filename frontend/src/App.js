import React, { useState, useEffect } from 'react';
import './App.css';
import { 
  UserSearchModal, 
  CreateEventModal, 
  EditEventModal,
  CreateOrganizationModal, 
  CreateCapoPromoterModal, 
  OrganizationDetailsModal 
} from './Modals';

function App() {
  const [events, setEvents] = useState([]);
  const [showEventDetails, setShowEventDetails] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [currentUser, setCurrentUser] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const [bookingType, setBookingType] = useState('');
  const [partySize, setPartySize] = useState(1);
  const [showChat, setShowChat] = useState(false);
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [currentView, setCurrentView] = useState('main'); // main, promoter, capo-promoter, clubly-founder
  const [showUserSetup, setShowUserSetup] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  
  // New states for enhanced features
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [selectedUserProfile, setSelectedUserProfile] = useState(null);
  const [showUserSearch, setShowUserSearch] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [showCreateEvent, setShowCreateEvent] = useState(false);
  const [showEditEvent, setShowEditEvent] = useState(false);
  const [selectedEventToEdit, setSelectedEventToEdit] = useState(null);
  const [showCreateOrganization, setShowCreateOrganization] = useState(false);
  const [showCreateCapoPromoter, setShowCreateCapoPromoter] = useState(false);
  const [showOrganizationDetails, setShowOrganizationDetails] = useState(false);
  const [selectedOrganization, setSelectedOrganization] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchEvents();
    checkAuthStatus();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchChats();
    }
  }, [currentUser]);

  useEffect(() => {
    if (currentUser && currentView !== 'main') {
      fetchDashboardData();
    }
  }, [currentView, currentUser]);

  const fetchDashboardData = async () => {
    if (!currentUser || currentView === 'main') return;
    
    try {
      let endpoint;
      switch (currentView) {
        case 'promoter':
          endpoint = '/api/dashboard/promoter';
          break;
        case 'capo-promoter':
          endpoint = '/api/dashboard/capo-promoter';
          break;
        case 'clubly-founder':
          endpoint = '/api/dashboard/clubly-founder';
          break;
        default:
          return;
      }
      
      const response = await fetch(`${backendUrl}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        console.error('Failed to fetch dashboard data');
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  useEffect(() => {
    if (currentUser && currentView !== 'main') {
      fetchDashboardData();
    }
  }, [currentView, currentUser]);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await fetch(`${backendUrl}/api/user/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const user = await response.json();
          setCurrentUser(user);
          
          // Check if user needs setup
          if (user.needs_setup) {
            setShowUserSetup(true);
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/events`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Errore nel caricamento eventi:', error);
    }
  };

  const handleLogin = async (loginData, password) => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login: loginData, password })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setCurrentUser(data.user);
        setShowAuth(false);
        
        // Check if user needs setup
        if (data.user.needs_setup) {
          setShowUserSetup(true);
        } else if (selectedEvent) {
          setShowBooking(true);
        }
      } else {
        alert('Credenziali non valide');
      }
    } catch (error) {
      alert('Errore durante il login');
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        setCurrentUser(data.user);
        setShowAuth(false);
        if (selectedEvent) {
          setShowBooking(true);
        }
      } else {
        const error = await response.json();
        alert(error.message || 'Errore durante la registrazione');
      }
    } catch (error) {
      alert('Errore durante la registrazione');
    }
  };

  const handleUserSetup = async (setupData) => {
    try {
      const response = await fetch(`${backendUrl}/api/user/setup`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(setupData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data.user);
        setShowUserSetup(false);
        alert('Profilo completato con successo!');
      } else {
        const error = await response.json();
        alert(error.detail || 'Errore durante la configurazione del profilo');
      }
    } catch (error) {
      alert('Errore durante la configurazione del profilo');
    }
  };

  const handleBookNow = (event) => {
    setSelectedEvent(event);
    if (!currentUser) {
      setShowAuth(true);
    } else {
      setShowBooking(true);
    }
  };

  const handleBookingSubmit = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/bookings`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          event_id: selectedEvent.id,
          booking_type: bookingType,
          party_size: partySize
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert('Prenotazione inviata! Chat con promoter avviata.');
        setShowBooking(false);
        setSelectedEvent(null);
        fetchEvents(); // Refresh to update availability
        fetchChats(); // Fetch new chat
        setShowChat(true); // Open chat interface
      }
    } catch (error) {
      alert('Errore durante la prenotazione');
    }
  };

  const fetchChats = async () => {
    if (!currentUser) return;
    try {
      const response = await fetch(`${backendUrl}/api/user/chats`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setChats(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento chat:', error);
    }
  };

  const fetchChatMessages = async (chatId) => {
    try {
      const response = await fetch(`${backendUrl}/api/chats/${chatId}/messages`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setChatMessages(data);
      }
    } catch (error) {
      console.error('Errore nel caricamento messaggi:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChat) return;
    
    try {
      const response = await fetch(`${backendUrl}/api/chats/${selectedChat.id}/messages`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          chat_id: selectedChat.id,
          sender_id: currentUser.id,
          sender_role: currentUser.ruolo,
          message: newMessage 
        })
      });
      
      if (response.ok) {
        setNewMessage('');
        fetchChatMessages(selectedChat.id); // Refresh messages
      } else {
        console.error('Failed to send message');
        alert('Errore nell\'invio del messaggio');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Errore nell\'invio del messaggio');
    }
  };

  // New functions for enhanced features
  const viewUserProfile = async (userId) => {
    try {
      const response = await fetch(`${backendUrl}/api/users/${userId}/profile`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const profile = await response.json();
        setSelectedUserProfile(profile);
        setShowUserProfile(true);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const openEditEvent = (event) => {
    setSelectedEventToEdit(event);
    setShowEditEvent(true);
  };

  const searchUsers = async (searchParams) => {
    try {
      const response = await fetch(`${backendUrl}/api/users/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(searchParams)
      });
      
      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      }
    } catch (error) {
      console.error('Error searching users:', error);
    }
  };

  const createEventByPromoter = async (eventData) => {
    try {
      const response = await fetch(`${backendUrl}/api/events/create-by-promoter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(eventData)
      });
      
      if (response.ok) {
        const result = await response.json();
        alert('Evento creato con successo!');
        setShowCreateEvent(false);
        fetchDashboardData(); // Refresh dashboard data
        fetchEvents(); // Refresh events list
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Errore durante la creazione dell\'evento');
    }
  };

  const updateEvent = async (eventId, eventData) => {
    try {
      const response = await fetch(`${backendUrl}/api/events/${eventId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(eventData)
      });
      
      if (response.ok) {
        alert('Evento aggiornato con successo!');
        setShowEditEvent(false);
        setSelectedEventToEdit(null);
        fetchDashboardData(); // Refresh dashboard data
        fetchEvents(); // Refresh events list
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Errore durante l\'aggiornamento dell\'evento');
    }
  };

  const createEventByFounder = async (eventData) => {
    try {
      const response = await fetch(`${backendUrl}/api/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(eventData)
      });
      
      if (response.ok) {
        const result = await response.json();
        alert('Evento creato con successo!');
        setShowCreateEvent(false);
        fetchDashboardData(); // Refresh dashboard data
        fetchEvents(); // Refresh events list
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Errore durante la creazione dell\'evento');
    }
  };

  const createOrganization = async (orgData) => {
    try {
      const response = await fetch(`${backendUrl}/api/organizations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(orgData)
      });
      
      if (response.ok) {
        const result = await response.json();
        alert('Organizzazione creata con successo!');
        setShowCreateOrganization(false);
        fetchDashboardData(); // Refresh dashboard data
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating organization:', error);
      alert('Errore durante la creazione dell\'organizzazione');
    }
  };

  const createCapoPromoter = async (userData) => {
    try {
      const response = await fetch(`${backendUrl}/api/users/temporary-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...userData,
          ruolo: 'capo_promoter'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Capo Promoter creato con successo!\nEmail: ${result.email}\nPassword temporanea: ${result.temporary_password}`);
        setShowCreateCapoPromoter(false);
        fetchDashboardData(); // Refresh dashboard data
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating capo promoter:', error);
      alert('Errore durante la creazione del capo promoter');
    }
  };

  const viewOrganizationDetails = async (orgId) => {
    try {
      const response = await fetch(`${backendUrl}/api/organizations/${orgId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const org = await response.json();
        setSelectedOrganization(org);
        setShowOrganizationDetails(true);
      }
    } catch (error) {
      console.error('Error fetching organization details:', error);
    }
  };

  const openChat = (chat) => {
    setSelectedChat(chat);
    fetchChatMessages(chat.id);
  };

  // Dashboard Components
  const PromoterDashboard = () => {
    if (!dashboardData) return <div className="text-white">Caricamento...</div>;
    
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8 flex items-center">
          🎪 Dashboard Promoter
          <span className="ml-4 text-gray-400 text-lg">Organizzazione: {dashboardData.organization}</span>
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Eventi dell'organizzazione */}
          <div className="bg-gray-900 border border-red-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">🎉 Eventi dell'Organizzazione</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {dashboardData.events?.map(event => (
                <div key={event.id} className="bg-gray-800 rounded-lg p-3">
                  <h4 className="text-white font-bold">{event.name}</h4>
                  <p className="text-gray-300 text-sm">📅 {event.date}</p>
                  <p className="text-gray-300 text-sm">📍 {event.location}</p>
                </div>
              ))}
            </div>
            <button 
              onClick={() => setShowCreateEvent(true)}
              className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
            >
              ➕ Crea Evento
            </button>
          </div>

          {/* Membri del team */}
          <div className="bg-gray-900 border border-blue-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">👥 Team Organizzazione</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {dashboardData.members?.map(member => (
                <div 
                  key={member.id} 
                  onClick={() => viewUserProfile(member.id)}
                  className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {member.profile_image && (
                      <img 
                        src={member.profile_image} 
                        alt={member.nome}
                        className="w-8 h-8 rounded-full object-cover"
                      />
                    )}
                    <div>
                      <p className="text-white font-bold">@{member.username}</p>
                      <p className="text-gray-300 text-sm">
                        {member.ruolo === 'capo_promoter' ? '🎯' : '🎪'} {member.nome} {member.cognome}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chat attive */}
          <div className="bg-gray-900 border border-green-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">💬 Chat Attive</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {dashboardData.chats?.slice(0, 5).map(chat => (
                <div key={chat.id} className="bg-gray-800 rounded-lg p-3">
                  <p className="text-white font-bold">{chat.client?.nome}</p>
                  <p className="text-gray-300 text-sm">{chat.event?.name}</p>
                  {chat.last_message && (
                    <p className="text-gray-400 text-xs truncate">
                      {chat.last_message.message.substring(0, 40)}...
                    </p>
                  )}
                </div>
              ))}
            </div>
            <button 
              onClick={() => setShowChat(true)}
              className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
            >
              💬 Apri Chat
            </button>
          </div>
        </div>

        {/* User Search Section */}
        <div className="mt-8 bg-gray-900 border border-purple-600 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">🔍 Ricerca Utenti</h3>
          <button 
            onClick={() => setShowUserSearch(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded font-bold transition-colors"
          >
            Cerca Utenti Clubly
          </button>
        </div>
      </div>
    );
  };

  const CapoPromoterDashboard = () => {
    if (!dashboardData) return <div className="text-white">Caricamento...</div>;
    
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8 flex items-center">
          🎯 Dashboard Capo Promoter
          <span className="ml-4 text-gray-400 text-lg">Organizzazione: {dashboardData.organization}</span>
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Gestione eventi */}
          <div className="bg-gray-900 border border-red-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">🎉 Gestione Eventi</h3>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {dashboardData.events?.map(event => (
                <div 
                  key={event.id} 
                  className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors border-l-4 border-transparent hover:border-orange-500"
                  onClick={() => openEditEvent(event)}
                  title="Clicca per modificare questo evento"
                >
                  <h4 className="text-white font-bold">{event.name}</h4>
                  <p className="text-gray-300 text-sm">📅 {event.date}</p>
                  <p className="text-gray-300 text-sm">📍 {event.location}</p>
                  <p className="text-orange-400 text-xs mt-1">👆 Clicca per modificare</p>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <button 
                onClick={() => setShowCreateEvent(true)}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
              >
                ➕ Crea Evento
              </button>
            </div>
          </div>

          {/* Team organizzazione */}
          <div className="bg-gray-900 border border-blue-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">👥 Team Organizzazione</h3>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {dashboardData.members?.map(member => (
                <div 
                  key={member.id}
                  onClick={() => viewUserProfile(member.id)}
                  className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {member.profile_image && (
                      <img 
                        src={member.profile_image} 
                        alt={member.nome}
                        className="w-8 h-8 rounded-full object-cover"
                      />
                    )}
                    <div>
                      <p className="text-white font-bold">@{member.username}</p>
                      <p className="text-gray-300 text-sm">
                        {member.ruolo === 'capo_promoter' ? '🎯' : '🎪'} {member.nome} {member.cognome}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <button 
              onClick={() => alert('Funzione in sviluppo: Crea Credenziali Promoter')}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
            >
              🆔 Crea Credenziali
            </button>
          </div>

          {/* Chat attive */}
          <div className="bg-gray-900 border border-green-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">💬 Chat Attive</h3>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {dashboardData.chats?.slice(0, 5).map(chat => (
                <div key={chat.id} className="bg-gray-800 rounded-lg p-3">
                  <p className="text-white font-bold">{chat.client?.nome}</p>
                  <p className="text-gray-300 text-sm">{chat.event?.name}</p>
                  {chat.last_message && (
                    <p className="text-gray-400 text-xs truncate">
                      {chat.last_message.message.substring(0, 40)}...
                    </p>
                  )}
                </div>
              ))}
            </div>
            <button 
              onClick={() => setShowChat(true)}
              className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
            >
              💬 Apri Chat
            </button>
          </div>
        </div>

        {/* User Search Section */}
        <div className="mt-8 bg-gray-900 border border-purple-600 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">🔍 Ricerca Utenti</h3>
          <button 
            onClick={() => setShowUserSearch(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded font-bold transition-colors"
          >
            Cerca Utenti Clubly
          </button>
        </div>

        {/* Permessi aggiuntivi */}
        <div className="mt-8 bg-gray-900 border border-yellow-600 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">⚡ Permessi Speciali</h3>
          <p className="text-gray-300 mb-4">Come Capo Promoter hai accesso a funzionalità avanzate di gestione.</p>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 bg-gray-800 rounded-lg p-4 border-l-4 border-yellow-500">
              <div className="w-10 h-10 bg-yellow-600 rounded-full flex items-center justify-center">
                <span className="text-black font-bold">✏️</span>
              </div>
              <div>
                <h4 className="text-white font-semibold">Modifica Eventi</h4>
                <p className="text-gray-400 text-sm">Puoi modificare: Nome evento, Line-up DJ e Orario di inizio</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">👥</span>
              </div>
              <div>
                <h4 className="text-white font-semibold">Gestione Team</h4>
                <p className="text-gray-400 text-sm">Visualizza e gestisci i membri della tua organizzazione</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 bg-gray-800 rounded-lg p-4 border-l-4 border-green-500">
              <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">🆔</span>
              </div>
              <div>
                <h4 className="text-white font-semibold">Crea Promoter</h4>
                <p className="text-gray-400 text-sm">Crea nuovi account promoter per la tua organizzazione</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ClublyFounderDashboard = () => {
    if (!dashboardData) return <div className="text-white">Caricamento...</div>;
    
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8 flex items-center">
          👑 Dashboard Clubly Founder
          <span className="ml-4 text-gray-400 text-lg">Controllo Totale</span>
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Statistiche */}
          <div className="bg-gray-900 border border-gold-500 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">📊 Statistiche Piattaforma</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Organizzazioni:</span>
                <span className="text-white font-bold">{dashboardData.organizations?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Eventi Totali:</span>
                <span className="text-white font-bold">{dashboardData.events?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Capi Promoter:</span>
                <span className="text-white font-bold">{dashboardData.users?.capo_promoter?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Promoter:</span>
                <span className="text-white font-bold">{dashboardData.users?.promoter?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Clienti:</span>
                <span className="text-white font-bold">{dashboardData.users?.cliente || 0}</span>
              </div>
            </div>
          </div>

          {/* Organizzazioni */}
          <div className="bg-gray-900 border border-blue-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">🏢 Organizzazioni</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {dashboardData.organizations?.map(org => (
                <div 
                  key={org.id} 
                  onClick={() => viewOrganizationDetails(org.id)}
                  className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  <p className="text-white font-bold">{org.name}</p>
                  <p className="text-gray-400 text-sm">📍 {org.location}</p>
                </div>
              ))}
            </div>
            <button 
              onClick={() => setShowCreateOrganization(true)}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
            >
              ➕ Crea Organizzazione
            </button>
          </div>

          {/* Gestione utenti */}
          <div className="bg-gray-900 border border-green-600 rounded-lg p-6">
            <h3 className="text-xl font-bold text-white mb-4">👥 Gestione Utenti</h3>
            <div className="space-y-3">
              <div className="bg-gray-800 rounded-lg p-3">
                <p className="text-white font-bold">Capi Promoter</p>
                <div className="mt-2 space-y-1">
                  {dashboardData.users?.capo_promoter?.slice(0, 3).map(user => (
                    <div 
                      key={user.id}
                      onClick={() => viewUserProfile(user.id)}
                      className="text-gray-400 text-sm cursor-pointer hover:text-white transition-colors"
                    >
                      • @{user.username} - {user.nome} {user.cognome}
                    </div>
                  ))}
                </div>
              </div>
              <button 
                onClick={() => setShowCreateCapoPromoter(true)}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-bold transition-colors w-full"
              >
                ➕ Crea Capo Promoter
              </button>
            </div>
          </div>
        </div>

        {/* User Search Section */}
        <div className="mt-8 bg-gray-900 border border-purple-600 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">🔍 Ricerca Utenti</h3>
          <button 
            onClick={() => setShowUserSearch(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded font-bold transition-colors"
          >
            Cerca Utenti Clubly
          </button>
        </div>

        {/* Eventi recenti */}
        <div className="mt-8 bg-gray-900 border border-red-600 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">🎉 Tutti gli Eventi</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            {dashboardData.events?.slice(0, 6).map(event => (
              <div key={event.id} className="bg-gray-800 rounded-lg p-4">
                <h4 className="text-white font-bold">{event.name}</h4>
                <p className="text-gray-300 text-sm">🏢 {event.organization}</p>
                <p className="text-gray-300 text-sm">📍 {event.location}</p>
                <p className="text-gray-300 text-sm">📅 {event.date}</p>
              </div>
            ))}
          </div>
          <button 
            onClick={() => setShowCreateEvent(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded font-bold transition-colors"
          >
            ➕ Crea Nuovo Evento
          </button>
        </div>
      </div>
    );
  };

  const EventCard = ({ event }) => (
    <div className="bg-gray-900 border border-red-600 rounded-lg overflow-hidden shadow-lg hover:shadow-red-500/20 transition-all duration-300 transform hover:scale-105">
      <div className="h-48 bg-gradient-to-br from-red-600 to-black relative overflow-hidden">
        <img 
          src={event.image || 'https://images.pexels.com/photos/11748607/pexels-photo-11748607.jpeg'} 
          alt={event.name}
          className="w-full h-full object-cover opacity-80"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
        <div className="absolute bottom-4 left-4 text-white">
          <div className="bg-red-600 px-2 py-1 text-xs rounded font-bold">
            {new Date(event.date).toLocaleDateString('it-IT')}
          </div>
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-white font-bold text-lg mb-2">{event.name}</h3>
        <p className="text-gray-300 text-sm mb-2">📍 {event.location}</p>
        <div className="flex space-x-2">
          <button 
            onClick={() => handleBookNow(event)}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-bold text-sm flex-1 transition-colors"
          >
            Prenota Ora
          </button>
          <button 
            onClick={() => { setSelectedEvent(event); setShowEventDetails(true); }}
            className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded font-bold text-sm transition-colors"
          >
            Scopri di Più
          </button>
        </div>
      </div>
    </div>
  );

  const EventDetailsModal = () => (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-red-600 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="relative h-64">
          <img 
            src={selectedEvent?.image || 'https://images.pexels.com/photos/11748607/pexels-photo-11748607.jpeg'} 
            alt={selectedEvent?.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
          <button 
            onClick={() => setShowEventDetails(false)}
            className="absolute top-4 right-4 text-white bg-black/50 rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600 transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="p-6">
          <h2 className="text-white text-2xl font-bold mb-4">{selectedEvent?.name}</h2>
          <div className="space-y-3 text-gray-300">
            <p><span className="text-red-400">📅 Data:</span> {new Date(selectedEvent?.date).toLocaleDateString('it-IT', { 
              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
            })}</p>
            <p><span className="text-red-400">🕘 Orario:</span> {selectedEvent?.start_time}</p>
            <p><span className="text-red-400">📍 Luogo:</span> {selectedEvent?.location}</p>
            <p><span className="text-red-400">🏢 Organizzazione:</span> {selectedEvent?.organization}</p>
            {selectedEvent?.lineup && (
              <p><span className="text-red-400">🎵 Line-up:</span> {selectedEvent.lineup.join(', ')}</p>
            )}
            {selectedEvent?.guests && (
              <p><span className="text-red-400">⭐ Guest:</span> {selectedEvent.guests.join(', ')}</p>
            )}
          </div>
          
          {selectedEvent?.tables_available > 0 && (
            <div className="mt-6">
              <h3 className="text-white font-bold mb-2">Disponibilità Tavoli</h3>
              <div className="bg-gray-800 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-300">Tavoli disponibili</span>
                  <span className="text-red-400 font-bold">{selectedEvent.tables_available}/{selectedEvent.total_tables}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-red-600 to-red-400 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${(selectedEvent.tables_available / selectedEvent.total_tables) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}
          
          <button 
            onClick={() => handleBookNow(selectedEvent)}
            className="w-full bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg font-bold text-lg mt-6 transition-colors"
          >
            Prenota Ora
          </button>
        </div>
      </div>
    </div>
  );

  const AuthModal = () => {
    const [formData, setFormData] = useState({
      login: '', password: '', nome: '', cognome: '', username: '', 
      data_nascita: '', citta: '', profile_image: ''
    });
    const [imagePreview, setImagePreview] = useState(null);

    const handleImageUpload = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setFormData({...formData, profile_image: reader.result});
          setImagePreview(reader.result);
        };
        reader.readAsDataURL(file);
      }
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      if (authMode === 'login') {
        handleLogin(formData.login, formData.password);
      } else {
        const registerData = {
          nome: formData.nome,
          cognome: formData.cognome,
          email: formData.login,
          username: formData.username,
          password: formData.password,
          data_nascita: formData.data_nascita,
          citta: formData.citta,
          profile_image: formData.profile_image
        };
        handleRegister(registerData);
      }
    };

    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 border border-red-600 rounded-xl max-w-md w-full shadow-2xl">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-white text-2xl font-bold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
                {authMode === 'login' ? 'Accedi a Clubly' : 'Unisciti a Clubly'}
              </h2>
              <button 
                onClick={() => setShowAuth(false)}
                className="text-gray-400 hover:text-red-400 text-2xl font-bold transition-colors"
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <input
                  type={authMode === 'login' ? 'text' : 'email'}
                  placeholder={authMode === 'login' ? 'Email o Username' : 'Email'}
                  value={formData.login}
                  onChange={(e) => setFormData({...formData, login: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                  required
                />
              </div>
              
              <div className="relative">
                <input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                  required
                />
              </div>
              
              {authMode === 'register' && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="text"
                      placeholder="Nome"
                      value={formData.nome}
                      onChange={(e) => setFormData({...formData, nome: e.target.value})}
                      className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Cognome"
                      value={formData.cognome}
                      onChange={(e) => setFormData({...formData, cognome: e.target.value})}
                      className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                      required
                    />
                  </div>
                  
                  <input
                    type="text"
                    placeholder="Username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                    required
                  />
                  
                  <input
                    type="date"
                    value={formData.data_nascita}
                    onChange={(e) => setFormData({...formData, data_nascita: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                    required
                  />
                  
                  <input
                    type="text"
                    placeholder="Città"
                    value={formData.citta}
                    onChange={(e) => setFormData({...formData, citta: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                    required
                  />
                  
                  {/* Profile Image Upload */}
                  <div className="space-y-2">
                    <label className="text-white text-sm font-medium">Foto Profilo (Opzionale)</label>
                    <div className="flex items-center space-x-4">
                      {imagePreview && (
                        <img 
                          src={imagePreview} 
                          alt="Preview" 
                          className="w-16 h-16 rounded-full object-cover border-2 border-red-500"
                        />
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-red-600 file:text-white hover:file:bg-red-700 file:cursor-pointer"
                      />
                    </div>
                  </div>
                </>
              )}
              
              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                {authMode === 'login' ? '🔐 Accedi' : '🎉 Registrati'}
              </button>
            </form>
            
            <div className="mt-6 text-center">
              <button 
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-red-400 hover:text-red-300 text-sm font-medium transition-colors"
              >
                {authMode === 'login' ? '✨ Non hai un account? Registrati ora' : '👋 Hai già un account? Accedi'}
              </button>
            </div>
            
            {authMode === 'login' && (
              <div className="mt-4 p-3 bg-gray-800 rounded-lg border border-gray-700">
                <p className="text-gray-300 text-xs text-center">
                  <span className="text-red-400 font-medium">Demo:</span> admin / admin123 | capo_milano / Password1
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const UserSetupModal = () => {
    const [setupData, setSetupData] = useState({
      cognome: '', username: '', data_nascita: '', citta: '', profile_image: '', biografia: ''
    });
    const [imagePreview, setImagePreview] = useState(null);

    const handleImageUpload = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setSetupData({...setupData, profile_image: reader.result});
          setImagePreview(reader.result);
        };
        reader.readAsDataURL(file);
      }
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      handleUserSetup(setupData);
    };

    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 border border-red-600 rounded-xl max-w-md w-full shadow-2xl">
          <div className="p-6">
            <div className="text-center mb-6">
              <h2 className="text-white text-2xl font-bold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
                Completa il tuo Profilo
              </h2>
              <p className="text-gray-400 text-sm mt-2">
                Ciao {currentUser?.nome}! Completa le informazioni per accedere alla piattaforma.
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Cognome"
                value={setupData.cognome}
                onChange={(e) => setSetupData({...setupData, cognome: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <input
                type="text"
                placeholder="Username"
                value={setupData.username}
                onChange={(e) => setSetupData({...setupData, username: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <div>
                <label className="text-white text-sm font-medium block mb-1">Data di Nascita</label>
                <input
                  type="date"
                  value={setupData.data_nascita}
                  onChange={(e) => setSetupData({...setupData, data_nascita: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                  required
                />
              </div>
              
              <input
                type="text"
                placeholder="Città"
                value={setupData.citta}
                onChange={(e) => setSetupData({...setupData, citta: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <textarea
                placeholder="Biografia (Opzionale)"
                value={setupData.biografia}
                onChange={(e) => setSetupData({...setupData, biografia: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                rows="3"
              />
              
              {/* Profile Image Upload */}
              <div className="space-y-2">
                <label className="text-white text-sm font-medium">Foto Profilo (Opzionale)</label>
                <div className="flex items-center space-x-4">
                  {imagePreview && (
                    <img 
                      src={imagePreview} 
                      alt="Preview" 
                      className="w-16 h-16 rounded-full object-cover border-2 border-red-500"
                    />
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-red-600 file:text-white hover:file:bg-red-700 file:cursor-pointer"
                  />
                </div>
              </div>
              
              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                🎯 Completa Configurazione
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // New Modal Components
  const UserProfileModal = () => {
    if (!selectedUserProfile) return null;

    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 border border-red-600 rounded-xl max-w-md w-full shadow-2xl">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-white text-2xl font-bold">Profilo Utente</h2>
              <button 
                onClick={() => setShowUserProfile(false)}
                className="text-gray-400 hover:text-red-400 text-2xl font-bold transition-colors"
              >
                ✕
              </button>
            </div>
            
            <div className="text-center mb-6">
              {selectedUserProfile.profile_image ? (
                <img 
                  src={selectedUserProfile.profile_image} 
                  alt="Profile" 
                  className="w-24 h-24 rounded-full object-cover mx-auto border-4 border-red-500"
                />
              ) : (
                <div className="w-24 h-24 bg-red-600 rounded-full flex items-center justify-center mx-auto">
                  <span className="text-white text-3xl font-bold">
                    {selectedUserProfile.nome?.charAt(0)}
                  </span>
                </div>
              )}
              <h3 className="text-white text-xl font-bold mt-4">
                {selectedUserProfile.nome} {selectedUserProfile.cognome}
              </h3>
              <p className="text-gray-400">@{selectedUserProfile.username}</p>
            </div>
            
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="text-red-400 font-bold mb-2">📍 Informazioni</h4>
                <p className="text-gray-300"><span className="text-gray-400">Città:</span> {selectedUserProfile.citta}</p>
                <p className="text-gray-300"><span className="text-gray-400">Ruolo:</span> {
                  selectedUserProfile.ruolo === 'clubly_founder' ? '👑 Clubly Founder' :
                  selectedUserProfile.ruolo === 'capo_promoter' ? '🎯 Capo Promoter' :
                  selectedUserProfile.ruolo === 'promoter' ? '🎪 Promoter' : '🎉 Cliente'
                }</p>
                {selectedUserProfile.organization && (
                  <p className="text-gray-300"><span className="text-gray-400">Organizzazione:</span> {selectedUserProfile.organization}</p>
                )}
              </div>
              
              {selectedUserProfile.biografia && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <h4 className="text-red-400 font-bold mb-2">📝 Biografia</h4>
                  <p className="text-gray-300">{selectedUserProfile.biografia}</p>
                </div>
              )}
              
              <div className="bg-gray-800 rounded-lg p-4">
                <h4 className="text-red-400 font-bold mb-2">📅 Membro da</h4>
                <p className="text-gray-300">
                  {new Date(selectedUserProfile.created_at).toLocaleDateString('it-IT', {
                    year: 'numeric', month: 'long', day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const BookingModal = () => (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-red-600 rounded-lg max-w-md w-full">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-xl font-bold">Prenota per {selectedEvent?.name}</h2>
            <button 
              onClick={() => setShowBooking(false)}
              className="text-gray-400 hover:text-red-400 text-xl"
            >
              ✕
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="text-white font-bold block mb-2">Tipo di Prenotazione</label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input 
                    type="radio" 
                    name="bookingType" 
                    value="lista"
                    onChange={(e) => setBookingType(e.target.value)}
                    className="text-red-600" 
                  />
                  <span className="text-gray-300">Lista / Prevendita</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input 
                    type="radio" 
                    name="bookingType" 
                    value="tavolo"
                    onChange={(e) => setBookingType(e.target.value)}
                    className="text-red-600" 
                  />
                  <span className="text-gray-300">Tavolo</span>
                </label>
              </div>
            </div>
            
            <div>
              <label className="text-white font-bold block mb-2">Numero di Persone</label>
              <select 
                value={partySize}
                onChange={(e) => setPartySize(parseInt(e.target.value))}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white focus:border-red-600 outline-none"
              >
                {[...Array(selectedEvent?.max_party_size || 10)].map((_, i) => (
                  <option key={i+1} value={i+1}>
                    {i+1} {i === 0 ? 'persona' : 'persone'}
                  </option>
                ))}
              </select>
            </div>
            
            <button 
              onClick={handleBookingSubmit}
              disabled={!bookingType}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white py-3 rounded font-bold transition-colors"
            >
              Conferma Prenotazione
            </button>
            
            <p className="text-gray-400 text-sm text-center">
              Un promoter ti contatterà presto per finalizzare la prenotazione
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const ChatModal = () => {
    const [messageText, setMessageText] = useState('');
    const [isSending, setIsSending] = useState(false);

    // Improved message sending function
    const handleSendMessage = async () => {
      if (!messageText.trim() || !selectedChat || isSending) return;
      
      setIsSending(true);
      try {
        const response = await fetch(`${backendUrl}/api/chats/${selectedChat.id}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            chat_id: selectedChat.id,
            sender_id: currentUser.id,
            sender_role: currentUser.ruolo,
            message: messageText
          })
        });
        
        if (response.ok) {
          setMessageText('');
          await fetchChatMessages(selectedChat.id);
        } else {
          console.error('Failed to send message');
        }
      } catch (error) {
        console.error('Error sending message:', error);
      } finally {
        setIsSending(false);
      }
    };

    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    };

    return (
      <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 border border-red-600 rounded-lg w-full max-w-5xl h-[85vh] flex">
          {/* Chat List Sidebar */}
          <div className="w-1/3 border-r border-red-600 flex flex-col">
            <div className="p-4 border-b border-red-600">
              <div className="flex justify-between items-center">
                <h2 className="text-white text-xl font-bold">💬 Le Tue Chat</h2>
                <button 
                  onClick={() => setShowChat(false)}
                  className="text-gray-400 hover:text-red-400 text-xl"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto">
              {chats.map(chat => (
                <div 
                  key={chat.id} 
                  onClick={() => openChat(chat)}
                  className={`p-4 border-b border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors ${
                    selectedChat?.id === chat.id ? 'bg-red-600/20' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                      {chat.other_participant?.profile_image ? (
                        <img 
                          src={chat.other_participant.profile_image} 
                          alt="Profile"
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <span className="text-white font-bold">
                          {chat.other_participant?.nome?.charAt(0) || '?'}
                        </span>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 
                          className="text-white font-semibold cursor-pointer hover:text-red-400 transition-colors"
                          onClick={() => viewUserProfile(chat.other_participant?.id)}
                        >
                          @{chat.other_participant?.username}
                        </h3>
                        <span className="text-xs bg-gray-700 px-2 py-1 rounded">
                          {chat.participant_role === 'promoter' ? '🎪' : '🎉'}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm">{chat.event?.name}</p>
                      {chat.last_message && (
                        <p className="text-gray-500 text-xs truncate">
                          {chat.last_message.message.substring(0, 50)}...
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {chats.length === 0 && (
                <div className="p-4 text-center text-gray-400">
                  Nessuna chat disponibile
                </div>
              )}
            </div>
          </div>
          
          {/* Chat Messages Area */}
          <div className="flex-1 flex flex-col">
            {selectedChat ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-red-600 bg-gray-800">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                      {selectedChat.other_participant?.profile_image ? (
                        <img 
                          src={selectedChat.other_participant.profile_image} 
                          alt="Profile"
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <span className="text-white font-bold">
                          {selectedChat.other_participant?.nome?.charAt(0) || '?'}
                        </span>
                      )}
                    </div>
                    <div>
                      <h3 
                        className="text-white font-semibold cursor-pointer hover:text-red-400 transition-colors"
                        onClick={() => viewUserProfile(selectedChat.other_participant?.id)}
                      >
                        @{selectedChat.other_participant?.username}
                      </h3>
                      <p className="text-gray-400 text-sm">
                        {selectedChat.participant_role === 'promoter' ? '🎪 Promoter' : '🎉 Cliente'} • {selectedChat.event?.name}
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map(message => (
                    <div 
                      key={message.id} 
                      className={`flex ${message.sender_id === currentUser.id ? 'justify-end' : 'justify-start'}`}
                    >
                      <div 
                        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                          message.sender_id === currentUser.id 
                            ? 'bg-red-600 text-white rounded-br-sm' 
                            : 'bg-gray-700 text-white rounded-bl-sm'
                        }`}
                      >
                        <p className="whitespace-pre-wrap break-words">{message.message}</p>
                        <p className="text-xs opacity-75 mt-2">
                          {new Date(message.timestamp).toLocaleTimeString('it-IT', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Message Input */}
                <div className="p-4 border-t border-red-600 bg-gray-800">
                  <div className="flex space-x-3">
                    <textarea
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Scrivi un messaggio... (Invio per inviare)"
                      className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none resize-none"
                      rows="2"
                      disabled={isSending}
                    />
                    <button 
                      onClick={handleSendMessage}
                      disabled={!messageText.trim() || isSending}
                      className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-bold transition-colors flex items-center space-x-2"
                    >
                      {isSending ? (
                        <>
                          <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                          <span>Invio...</span>
                        </>
                      ) : (
                        <>
                          <span>📤</span>
                          <span>Invia</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">💬</div>
                  <p className="text-gray-400 text-lg">Seleziona una chat per iniziare</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-red-600">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-red-500">CLUBLY</h1>
              
              {currentUser && (
                <div 
                  className="flex items-center space-x-2 cursor-pointer hover:bg-gray-800 rounded-lg p-2 transition-colors"
                  onClick={() => viewUserProfile(currentUser.id)}
                  title="Clicca per visualizzare il tuo profilo"
                >
                  {currentUser.profile_image ? (
                    <img 
                      src={currentUser.profile_image} 
                      alt="Profile" 
                      className="w-10 h-10 rounded-full object-cover border-2 border-red-500"
                    />
                  ) : (
                    <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center border-2 border-red-500">
                      <span className="text-white font-bold">{currentUser.nome?.charAt(0)}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-1">
                    <span className="text-gray-300 text-sm">
                      {currentUser.ruolo === 'clubly_founder' ? '👑' : 
                       currentUser.ruolo === 'capo_promoter' ? '🎯' :
                       currentUser.ruolo === 'promoter' ? '🎪' : '🎉'}
                    </span>
                    <span className="text-gray-300">Ciao, {currentUser.nome}!</span>
                  </div>
                </div>
              )}
            </div>
            
            {currentUser ? (
              <div className="flex items-center space-x-4">
                {currentUser.ruolo !== 'cliente' && currentView === 'main' && (
                  <button 
                    onClick={() => setCurrentView(
                      currentUser.ruolo === 'promoter' ? 'promoter' :
                      currentUser.ruolo === 'capo_promoter' ? 'capo-promoter' :
                      currentUser.ruolo === 'clubly_founder' ? 'clubly-founder' : 'main'
                    )}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded font-bold transition-colors"
                  >
                    🎛️ La Mia Dashboard
                  </button>
                )}
                
                {currentView !== 'main' && (
                  <button 
                    onClick={() => setCurrentView('main')}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded font-bold transition-colors"
                  >
                    🏠 Dashboard Principale
                  </button>
                )}
                
                <button 
                  onClick={() => setShowChat(true)}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded font-bold transition-colors relative"
                >
                  💬 Chat
                  {chats.length > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {chats.length}
                    </span>
                  )}
                </button>
                
                <button 
                  onClick={() => { 
                    localStorage.removeItem('token'); 
                    setCurrentUser(null); 
                    setChats([]); 
                    setCurrentView('main');
                  }}
                  className="text-red-400 hover:text-red-300"
                >
                  Esci
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setShowAuth(true)}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-bold transition-colors"
              >
                Accedi
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - Conditional Rendering based on currentView */}
      {currentView === 'main' ? (
        <>
          {/* Hero Section */}
          <section className="bg-gradient-to-br from-red-600 via-red-800 to-black py-16">
            <div className="container mx-auto px-4 text-center">
              <h2 className="text-4xl md:text-6xl font-bold mb-4">
                La Notte è <span className="text-red-400">NOSTRA</span>
              </h2>
              <p className="text-xl md:text-2xl text-gray-200 mb-8">
                Prenota i migliori eventi e tavoli nelle discoteche più esclusive
              </p>
            </div>
          </section>

          {/* Events Section */}
          <section className="py-16">
            <div className="container mx-auto px-4">
              <h2 className="text-3xl font-bold text-center mb-12">
                Eventi <span className="text-red-500">in Programma</span>
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {events.map(event => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
              
              {events.length === 0 && (
                <div className="text-center text-gray-400 py-16">
                  <p className="text-xl">Nessun evento disponibile al momento</p>
                  <p>Torna presto per scoprire i prossimi eventi!</p>
                </div>
              )}
            </div>
          </section>
        </>
      ) : (
        /* Dashboard Content */
        <>
          {currentView === 'promoter' && <PromoterDashboard />}
          {currentView === 'capo-promoter' && <CapoPromoterDashboard />}
          {currentView === 'clubly-founder' && <ClublyFounderDashboard />}
        </>
      )}

      {/* Modals */}
      {showEventDetails && selectedEvent && <EventDetailsModal />}
      {showAuth && <AuthModal />}
      {showUserSetup && <UserSetupModal />}
      {showBooking && selectedEvent && <BookingModal />}
      {showChat && <ChatModal />}
      {showUserProfile && <UserProfileModal />}
      
      {/* New Modals */}
      <UserSearchModal 
        show={showUserSearch}
        onClose={() => setShowUserSearch(false)}
        onSearch={searchUsers}
        searchResults={searchResults}
        onViewProfile={viewUserProfile}
      />
      
      <CreateEventModal 
        show={showCreateEvent}
        onClose={() => setShowCreateEvent(false)}
        onSubmit={createEventByPromoter}
      />
      
      <EditEventModal 
        show={showEditEvent}
        onClose={() => {
          setShowEditEvent(false);
          setSelectedEventToEdit(null);
        }}
        event={selectedEventToEdit}
        onSubmit={updateEvent}
      />
      
      <CreateOrganizationModal 
        show={showCreateOrganization}
        onClose={() => setShowCreateOrganization(false)}
        onSubmit={createOrganization}
      />
      
      <CreateCapoPromoterModal 
        show={showCreateCapoPromoter}
        onClose={() => setShowCreateCapoPromoter(false)}
        onSubmit={createCapoPromoter}
      />
      
      <OrganizationDetailsModal 
        show={showOrganizationDetails}
        onClose={() => setShowOrganizationDetails(false)}
        organization={selectedOrganization}
        onViewProfile={viewUserProfile}
      />
    </div>
  );
}

export default App;