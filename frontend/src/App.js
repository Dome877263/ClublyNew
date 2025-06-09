import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import Header from './Header';
import { 
  UserProfileModal,
  UserSearchModal, 
  CreateEventModal, 
  EditEventModal,
  CreateOrganizationModal, 
  CreateCapoPromoterModal,
  CreatePromoterModal,
  OrganizationDetailsModal,
  EditProfileModal,
  ChangePasswordModal,
  EditOrganizationModal
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
  
  // Enhanced states for new features
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [selectedUserProfile, setSelectedUserProfile] = useState(null);
  const [showOwnProfile, setShowOwnProfile] = useState(false);
  const [showUserSearch, setShowUserSearch] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [showCreateEvent, setShowCreateEvent] = useState(false);
  const [showEditEvent, setShowEditEvent] = useState(false);
  const [selectedEventToEdit, setSelectedEventToEdit] = useState(null);
  const [showCreateOrganization, setShowCreateOrganization] = useState(false);
  const [showCreateCapoPromoter, setShowCreateCapoPromoter] = useState(false);
  const [showCreatePromoter, setShowCreatePromoter] = useState(false);
  const [showOrganizationDetails, setShowOrganizationDetails] = useState(false);
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const [isLoadingChatMessages, setIsLoadingChatMessages] = useState(false);
  const [showEditOwnProfile, setShowEditOwnProfile] = useState(false);
  
  // NEW STATES FOR REQUIREMENTS
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [showEditOrganization, setShowEditOrganization] = useState(false);
  const [organizations, setOrganizations] = useState([]);
  const [availableCapoPromoters, setAvailableCapoPromoters] = useState([]);
  const [notificationsCount, setNotificationsCount] = useState(0);
  const [authError, setAuthError] = useState('');
  
  // Add ref for chat textarea to maintain focus
  const chatTextareaRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchEvents();
    checkAuthStatus();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchChats();
      fetchNotifications(); // Fetch notifications when user logs in
    }
  }, [currentUser]);

  useEffect(() => {
    if (currentUser && currentView !== 'main') {
      fetchDashboardData();
    }
  }, [currentView, currentUser]);

  // Fetch notifications count
  const fetchNotifications = async () => {
    if (!currentUser) return;
    try {
      const response = await fetch(`${backendUrl}/api/user/notifications`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setNotificationsCount(data.notification_count);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  // Fetch organizations for dropdowns
  const fetchOrganizations = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/organizations`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
    }
  };

  // Fetch available capo promoters
  const fetchAvailableCapoPromoters = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/organizations/available-capo-promoters`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableCapoPromoters(data);
      }
    } catch (error) {
      console.error('Error fetching available capo promoters:', error);
    }
  };

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
          // Check if user needs password change
          else if (user.needs_password_change) {
            setShowChangePassword(true);
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
      setAuthError(''); // Clear previous errors
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
        }
        // Check if user needs password change
        else if (data.user.needs_password_change) {
          setShowChangePassword(true);
        }
        else if (selectedEvent) {
          setShowBooking(true);
        }
      } else {
        const errorData = await response.json();
        setAuthError(errorData.detail || 'Email o password non corrette');
      }
    } catch (error) {
      setAuthError('Errore durante il login');
    }
  };

  const handleRegister = async (userData) => {
    try {
      setAuthError(''); // Clear previous errors
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
        setAuthError(error.detail || 'Errore durante la registrazione');
      }
    } catch (error) {
      setAuthError('Errore durante la registrazione');
    }
  };

  // Handle password change
  const handlePasswordChange = async (passwordData) => {
    try {
      const response = await fetch(`${backendUrl}/api/user/change-password`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(passwordData)
      });
      
      if (response.ok) {
        setShowChangePassword(false);
        alert('Password cambiata con successo!');
        // Update current user to reflect password change
        const updatedUser = {...currentUser, needs_password_change: false};
        setCurrentUser(updatedUser);
      } else {
        const error = await response.json();
        alert(error.detail || 'Errore durante il cambio password');
      }
    } catch (error) {
      alert('Errore durante il cambio password');
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
        
        // Check if user still needs password change after setup
        if (data.user.needs_password_change) {
          setShowChangePassword(true);
        } else {
          alert('Profilo completato con successo!');
        }
      } else {
        const error = await response.json();
        alert(error.detail || 'Errore durante la configurazione del profilo');
      }
    } catch (error) {
      alert('Errore durante la configurazione del profilo');
    }
  };

  const handleBookNow = async (event) => {
    setSelectedEvent(event);
    if (!currentUser) {
      setShowAuth(true);
    } else {
      // AUTO ASSIGNMENT - no manual promoter selection
      setShowBooking(true);
    }
  };

  // Updated booking submission - NO PROMOTER SELECTION
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
          // No selected_promoter_id - auto assignment
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Prenotazione inviata! Chat con ${result.promoter_name} avviata automaticamente.`);
        setShowBooking(false);
        setSelectedEvent(null);
        fetchEvents(); // Refresh to update availability
        fetchChats(); // Fetch new chat
        fetchNotifications(); // Update notifications
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

  const sendMessage = useCallback(async () => {
    if (!newMessage.trim() || !selectedChat) return;
    
    // Preserve textarea reference before sending
    const textareaElement = chatTextareaRef.current;
    
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
        fetchNotifications(); // Update notifications
        
        // ENHANCED: Maintain focus immediately and after DOM update
        if (textareaElement) {
          textareaElement.focus();
          // Double ensure focus after state update
          setTimeout(() => {
            textareaElement.focus();
            // Place cursor at end
            textareaElement.setSelectionRange(textareaElement.value.length, textareaElement.value.length);
          }, 0);
        }
      } else {
        console.error('Failed to send message');
        alert('Errore nell\'invio del messaggio');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Errore nell\'invio del messaggio');
    }
  }, [newMessage, selectedChat, currentUser, backendUrl]);

  // Enhanced functions for new features
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

  const openOwnProfile = () => {
    if (currentUser) {
      // Fetch fresh profile data when opening own profile
      fetch(`${backendUrl}/api/user/profile`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      .then(response => response.json())
      .then(profile => {
        setSelectedUserProfile(profile);
        setShowOwnProfile(true);
      })
      .catch(error => {
        console.error('Error fetching profile:', error);
        // Fallback to current user data
        setSelectedUserProfile(currentUser);
        setShowOwnProfile(true);
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    setCurrentView('main');
    setDashboardData(null);
    setChats([]);
    setChatMessages([]);
    setSelectedChat(null);
    setNotificationsCount(0);
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

  // Enhanced event creation handler
  const handleCreateEvent = (eventData, userRole) => {
    if (userRole === 'clubly_founder') {
      createEventByFounder(eventData);
    } else {
      createEventByPromoter(eventData);
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
        alert('Organizzazione creata con successo! Potrai assegnare un capo promoter successivamente.');
        setShowCreateOrganization(false);
        fetchDashboardData(); // Refresh dashboard data
        fetchOrganizations(); // Refresh organizations list
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating organization:', error);
      alert('Errore durante la creazione dell\'organizzazione');
    }
  };

  // Enhanced capo promoter creation with organization dropdown
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
        alert(`Capo Promoter creato con successo!\nEmail: ${result.email}\nPassword temporanea: ${result.temporary_password}\nOrganizzazione: ${result.organization || 'Da assegnare'}`);
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

  const createPromoter = async (userData) => {
    try {
      const response = await fetch(`${backendUrl}/api/users/temporary-credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...userData,
          ruolo: 'promoter'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Promoter creato con successo!\nEmail: ${result.email}\nPassword temporanea: ${result.temporary_password}`);
        setShowCreatePromoter(false);
        fetchDashboardData(); // Refresh dashboard data
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating promoter:', error);
      alert('Errore durante la creazione del promoter');
    }
  };

  // Organization editing function
  const editOrganization = async (orgId, orgData) => {
    try {
      const response = await fetch(`${backendUrl}/api/organizations/${orgId}/assign-capo-promoter`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(orgData)
      });
      
      if (response.ok) {
        alert('Organizzazione aggiornata con successo!');
        setShowEditOrganization(false);
        setSelectedOrganization(null);
        fetchDashboardData(); // Refresh dashboard data
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error editing organization:', error);
      alert('Errore durante la modifica dell\'organizzazione');
    }
  };

  // Profile editing function
  const editUserProfile = async (profileData) => {
    try {
      const response = await fetch(`${backendUrl}/api/user/profile/edit`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(profileData)
      });
      
      if (response.ok) {
        const result = await response.json();
        // Update current user data
        setCurrentUser(result.user);
        setSelectedUserProfile(result.user);
        setShowEditOwnProfile(false);
        alert('Profilo aggiornato con successo!');
      } else {
        const error = await response.json();
        alert(`Errore: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Errore durante l\'aggiornamento del profilo');
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

  // Enhanced organization details with edit functionality
  const openEditOrganization = async (org) => {
    setSelectedOrganization(org);
    await fetchAvailableCapoPromoters(); // Fetch available capo promoters
    setShowEditOrganization(true);
  };

  // Enhanced chat opening with proper state management
  const openChat = async (chat) => {
    // Clear previous chat state immediately
    setChatMessages([]);
    setSelectedChat(null);
    setIsLoadingChatMessages(true);
    
    try {
      // Set new chat
      setSelectedChat(chat);
      
      // Fetch new messages
      await fetchChatMessages(chat.id);
    } catch (error) {
      console.error('Error opening chat:', error);
    } finally {
      setIsLoadingChatMessages(false);
    }
  };

  // Enhanced message opening function for clickable usernames
  const handleUsernameClick = (senderId) => {
    if (senderId !== currentUser.id) {
      viewUserProfile(senderId);
    }
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
            {/* Removed "Crea Evento" button - only Clubly Founder can create events */}
            <div className="mt-4">
              <p className="text-gray-400 text-sm text-center italic">
                Gli eventi vengono creati dal Clubly Founder
              </p>
            </div>
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
              {/* Capo promoter non può creare eventi, solo modificarli */}
              <p className="text-gray-400 text-sm text-center italic">
                Come Capo Promoter puoi modificare gli eventi esistenti cliccando su di essi
              </p>
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
              onClick={() => setShowCreatePromoter(true)}
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
                <p className="text-gray-400 text-sm">Puoi modificare: Nome evento, Line-up DJ, Orario e Locandina</p>
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
                <div key={org.id} className="flex items-center justify-between bg-gray-800 rounded-lg p-3">
                  <div 
                    onClick={() => viewOrganizationDetails(org.id)}
                    className="flex-1 cursor-pointer hover:text-blue-400 transition-colors"
                  >
                    <p className="text-white font-bold">{org.name}</p>
                    <p className="text-gray-400 text-sm">📍 {org.location}</p>
                  </div>
                  <button
                    onClick={() => openEditOrganization(org)}
                    className="text-blue-400 hover:text-blue-300 text-sm bg-blue-900/20 px-2 py-1 rounded transition-colors"
                    title="Modifica organizzazione"
                  >
                    ✏️
                  </button>
                </div>
              ))}
            </div>
            <button 
              onClick={() => {
                fetchOrganizations();
                setShowCreateOrganization(true);
              }}
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
                onClick={() => {
                  fetchOrganizations();
                  setShowCreateCapoPromoter(true);
                }}
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
              <div key={event.id} className="bg-gray-800 rounded-lg p-4 flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="text-white font-bold">{event.name}</h4>
                  <p className="text-gray-300 text-sm">🏢 {event.organization}</p>
                  <p className="text-gray-300 text-sm">📍 {event.location}</p>
                  <p className="text-gray-300 text-sm">📅 {event.date}</p>
                </div>
                <div className="flex flex-col space-y-1 ml-2">
                  <button
                    onClick={() => openEditEvent(event)}
                    className="text-blue-400 hover:text-blue-300 text-xs bg-blue-900/20 px-2 py-1 rounded transition-colors"
                    title="Modifica evento"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => deleteEvent(event.id)}
                    className="text-red-400 hover:text-red-300 text-xs bg-red-900/20 px-2 py-1 rounded transition-colors"
                    title="Elimina evento"
                  >
                    🗑️
                  </button>
                </div>
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

  // DELETE EVENT FUNCTION FOR CLUBLY FOUNDER
  const deleteEvent = async (eventId) => {
    if (window.confirm('Sei sicuro di voler eliminare questo evento? Questa azione non può essere annullata.')) {
      try {
        const response = await fetch(`${backendUrl}/api/events/${eventId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          alert('Evento eliminato con successo!');
          fetchDashboardData(); // Refresh dashboard data
          fetchEvents(); // Refresh events list
        } else {
          const error = await response.json();
          alert(`Errore: ${error.detail}`);
        }
      } catch (error) {
        console.error('Error deleting event:', error);
        alert('Errore durante l\'eliminazione dell\'evento');
      }
    }
  };

  const EventCard = ({ event }) => (
    <div className="bg-gray-900 border border-red-600 rounded-lg overflow-hidden shadow-lg hover:shadow-red-500/20 transition-all duration-300 transform hover:scale-105">
      <div className="h-48 bg-gradient-to-br from-red-600 to-black relative overflow-hidden">
        <img 
          src={event.event_poster || event.image || 'https://images.pexels.com/photos/11748607/pexels-photo-11748607.jpeg'} 
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
            src={selectedEvent?.event_poster || selectedEvent?.image || 'https://images.pexels.com/photos/11748607/pexels-photo-11748607.jpeg'} 
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
            {selectedEvent?.end_time && (
              <p><span className="text-red-400">🕘 Fine:</span> {selectedEvent.end_time}</p>
            )}
            <p><span className="text-red-400">📍 Luogo:</span> {selectedEvent?.location}</p>
            {selectedEvent?.location_address && (
              <p><span className="text-red-400">🗺️ Indirizzo:</span> {selectedEvent.location_address}</p>
            )}
            <p><span className="text-red-400">🏢 Organizzazione:</span> {selectedEvent?.organization}</p>
            {selectedEvent?.lineup && selectedEvent.lineup.length > 0 && (
              <div>
                <span className="text-red-400">🎵 Line-up DJ:</span>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                  {selectedEvent.lineup.map((dj, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg px-3 py-2 border-l-4 border-red-500">
                      <div className="flex items-center space-x-2">
                        <span className="text-red-400">🎧</span>
                        <span className="text-white font-semibold">{dj}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {selectedEvent?.guests && selectedEvent.guests.length > 0 && (
              <div>
                <span className="text-red-400">⭐ Guest Speciali:</span>
                <div className="mt-2 space-y-2">
                  {selectedEvent.guests.map((guest, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg px-3 py-2 border-l-4 border-yellow-500">
                      <div className="flex items-center space-x-2">
                        <span className="text-yellow-400">⭐</span>
                        <span className="text-white font-semibold">{guest}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
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
                onClick={() => {
                  setShowAuth(false);
                  setAuthError('');
                }}
                className="text-gray-400 hover:text-red-400 text-2xl font-bold transition-colors"
              >
                ✕
              </button>
            </div>

            {/* ERROR MESSAGE */}
            {authError && (
              <div className="mb-4 p-3 bg-red-900/30 border border-red-600 rounded-lg">
                <p className="text-red-400 text-sm">{authError}</p>
              </div>
            )}
            
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
                onClick={() => {
                  setAuthMode(authMode === 'login' ? 'register' : 'login');
                  setAuthError('');
                }}
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

  // IMPROVED BOOKING MODAL - NO PROMOTER SELECTION
  const BookingModal = () => (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-red-600 rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
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
            {/* Event Info */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-red-400 font-bold mb-2">📅 Dettagli Evento</h3>
              <p className="text-gray-300 text-sm"><span className="text-gray-400">Data:</span> {selectedEvent?.date}</p>
              <p className="text-gray-300 text-sm"><span className="text-gray-400">Orario:</span> {selectedEvent?.start_time}</p>
              <p className="text-gray-300 text-sm"><span className="text-gray-400">Luogo:</span> {selectedEvent?.location}</p>
              <p className="text-gray-300 text-sm"><span className="text-gray-400">Organizzazione:</span> {selectedEvent?.organization}</p>
            </div>



            {/* Booking Type */}
            <div>
              <label className="text-white font-bold block mb-2">🎫 Tipo di prenotazione</label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors">
                  <input 
                    type="radio" 
                    value="lista" 
                    checked={bookingType === 'lista'} 
                    onChange={(e) => setBookingType(e.target.value)}
                    className="text-red-600" 
                  />
                  <span className="text-white">📝 Lista/Prevendita</span>
                </label>
                <label className="flex items-center space-x-2 bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors">
                  <input 
                    type="radio" 
                    value="tavolo" 
                    checked={bookingType === 'tavolo'} 
                    onChange={(e) => setBookingType(e.target.value)}
                    className="text-red-600" 
                  />
                  <span className="text-white">🍾 Tavolo</span>
                </label>
              </div>
            </div>

            {/* Party Size */}
            <div>
              <label className="text-white font-bold block mb-2">👥 Numero persone</label>
              <input
                type="number"
                min="1"
                max={selectedEvent?.max_party_size || 10}
                value={partySize}
                onChange={(e) => setPartySize(parseInt(e.target.value) || 1)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
              />
            </div>

            <button 
              onClick={handleBookingSubmit}
              disabled={!bookingType}
              className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white py-3 rounded-lg font-bold text-lg transition-colors disabled:cursor-not-allowed"
            >
              {!bookingType ? 'Seleziona tipo prenotazione' : '🎉 Conferma Prenotazione'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // ENHANCED CHAT MODAL 
  // Optimized ChatModal with better focus management and text direction
  const ChatModal = () => {
    // Enhanced auto-focus textarea when chat is selected
    useEffect(() => {
      if (selectedChat && chatTextareaRef.current) {
        // Multiple attempts to ensure focus
        const focusTextarea = () => {
          const textarea = chatTextareaRef.current;
          if (textarea) {
            textarea.focus();
            // Place cursor at end of text
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
          }
        };
        
        // Immediate focus
        focusTextarea();
        
        // Delayed focus to ensure DOM is ready
        setTimeout(focusTextarea, 50);
        setTimeout(focusTextarea, 150);
      }
    }, [selectedChat]);

    // Enhanced auto-focus when modal opens
    useEffect(() => {
      if (chatTextareaRef.current) {
        setTimeout(() => {
          chatTextareaRef.current.focus();
        }, 200);
      }
    }, []); // Run once when component mounts

    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 border border-green-600 rounded-xl max-w-4xl w-full h-[80vh] shadow-2xl">
          <div className="flex h-full">
            {/* Chat List */}
            <div className="w-1/3 border-r border-gray-700 p-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-white text-xl font-bold">💬 Chat</h3>
                <button 
                  onClick={() => setShowChat(false)}
                  className="text-gray-400 hover:text-green-400 text-xl font-bold transition-colors hover:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-2 h-full overflow-y-auto">
                {chats.map(chat => (
                  <div 
                    key={chat.id}
                    onClick={() => openChat(chat)}
                    className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedChat?.id === chat.id ? 
                      'bg-green-700 border border-green-500' : 
                      'bg-gray-800 hover:bg-gray-700 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      {/* Profile Image */}
                      {chat.other_participant?.profile_image ? (
                        <img 
                          src={chat.other_participant.profile_image} 
                          alt={chat.other_participant.nome}
                          className="w-10 h-10 rounded-full object-cover border-2 border-green-500"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center border-2 border-green-500">
                          <span className="text-white font-bold text-sm">
                            {chat.other_participant?.nome?.charAt(0)}
                          </span>
                        </div>
                      )}
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-semibold truncate">
                          {chat.other_participant?.nome} {chat.other_participant?.cognome}
                        </p>
                        <p className="text-gray-400 text-xs">
                          {chat.participant_role === 'promoter' ? '🎪' : '🎉'} 
                          @{chat.other_participant?.username}
                        </p>
                        <p className="text-gray-300 text-sm font-medium">
                          🎉 {chat.event?.name}
                        </p>
                        {chat.last_message && (
                          <p className="text-gray-400 text-xs truncate mt-1">
                            {chat.last_message.message.substring(0, 30)}...
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {chats.length === 0 && (
                  <div className="text-center text-gray-400 py-8">
                    <p>Nessuna chat attiva</p>
                    <p className="text-xs mt-2">Prenota un evento per iniziare una chat!</p>
                  </div>
                )}
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 flex flex-col">
              {selectedChat ? (
                <>
                  {/* Chat Header */}
                  <div className="border-b border-gray-700 p-4 bg-gray-800">
                    <div className="flex items-center space-x-3">
                      {selectedChat.other_participant?.profile_image ? (
                        <img 
                          src={selectedChat.other_participant.profile_image} 
                          alt={selectedChat.other_participant.nome}
                          className="w-12 h-12 rounded-full object-cover border-2 border-green-500"
                        />
                      ) : (
                        <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center border-2 border-green-500">
                          <span className="text-white font-bold">
                            {selectedChat.other_participant?.nome?.charAt(0)}
                          </span>
                        </div>
                      )}
                      <div>
                        <h4 className="text-white font-bold text-lg">
                          {selectedChat.other_participant?.nome} {selectedChat.other_participant?.cognome}
                        </h4>
                        <p className="text-gray-400 text-sm">
                          {selectedChat.participant_role === 'promoter' ? '🎪 Promoter' : '🎉 Cliente'} • 
                          @{selectedChat.other_participant?.username}
                        </p>
                        <p className="text-green-400 text-sm font-medium">
                          📅 {selectedChat.event?.name}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-800/30">
                    {isLoadingChatMessages ? (
                      <div className="text-center text-gray-400 py-8">
                        <p>Caricamento messaggi...</p>
                      </div>
                    ) : (
                      chatMessages.map(message => (
                        <div 
                          key={message.id} 
                          className={`flex ${message.sender_id === currentUser?.id ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-lg ${
                            message.sender_id === currentUser?.id ? 
                            'bg-green-600 text-white' : 
                            'bg-gray-700 text-gray-100'
                          }`}>
                            {message.sender_id !== currentUser?.id && (
                              <p 
                                className="text-green-400 text-xs font-semibold mb-1 cursor-pointer hover:text-green-300 transition-colors"
                                onClick={() => handleUsernameClick(message.sender_id)}
                              >
                                {selectedChat.other_participant?.nome} {selectedChat.other_participant?.cognome}
                              </p>
                            )}
                            <p className="text-sm leading-relaxed break-words">
                              {message.message}
                            </p>
                            <p className={`text-xs mt-2 ${
                              message.sender_id === currentUser?.id ? 'text-green-200' : 'text-gray-400'
                            }`}>
                              {new Date(message.timestamp).toLocaleTimeString('it-IT', { 
                                hour: '2-digit', minute: '2-digit' 
                              })}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Message Input - ENHANCED with better text direction handling */}
                  <div className="border-t border-gray-700 p-4 bg-gray-800">
                    <div className="flex space-x-3">
                      <textarea
                        ref={chatTextareaRef}
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                          }
                        }}
                        onFocus={() => {
                          // Ensure cursor is at the end when focused
                          const textarea = chatTextareaRef.current;
                          if (textarea) {
                            setTimeout(() => {
                              textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                            }, 0);
                          }
                        }}
                        placeholder="Scrivi un messaggio... (Premi Enter per inviare)"
                        className="chat-textarea flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none resize-none"
                        rows="2"
                        style={{ 
                          direction: 'ltr', 
                          textAlign: 'left',
                          unicodeBidi: 'normal',
                          writingMode: 'horizontal-tb'
                        }}
                        dir="ltr"
                        lang="it"
                        spellCheck="true"
                      />
                      <button 
                        onClick={sendMessage}
                        disabled={!newMessage.trim()}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-bold transition-colors disabled:cursor-not-allowed flex items-center space-x-2"
                      >
                        <span>📤</span>
                        <span>Invia</span>
                      </button>
                    </div>
                    <p className="text-gray-400 text-xs mt-2">
                      💡 Puoi usare Shift+Enter per andare a capo
                    </p>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center bg-gray-800/30">
                  <div className="text-center text-gray-400">
                    <div className="text-6xl mb-4">💬</div>
                    <p className="text-xl font-semibold">Seleziona una chat</p>
                    <p className="text-sm mt-2">Scegli una conversazione dalla lista per iniziare a chattare</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header with notifications badge and chat function */}
      <Header 
        currentUser={currentUser} 
        currentView={currentView} 
        setCurrentView={setCurrentView}
        onLogout={handleLogout}
        onOpenProfile={openOwnProfile}
        notificationsCount={notificationsCount}
        onOpenChat={() => setShowChat(true)} // FIXED: Properly opens chat modal
        onShowAuth={(mode) => {
          setAuthMode(mode);
          setShowAuth(true);
        }}
      />

      {/* Main Content */}
      {currentView === 'main' ? (
        <div className="container mx-auto px-4 py-8">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-red-600 to-red-400 bg-clip-text text-transparent">
              🎉 Clubly
            </h1>
            <p className="text-gray-300 text-xl">Scopri la vita notturna che ami</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map(event => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </div>
      ) : currentView === 'promoter' ? (
        <PromoterDashboard />
      ) : currentView === 'capo-promoter' ? (
        <CapoPromoterDashboard />
      ) : currentView === 'clubly-founder' ? (
        <ClublyFounderDashboard />
      ) : null}

      {/* Modals */}
      {showAuth && <AuthModal />}
      {showUserSetup && <UserSetupModal />}
      {showChangePassword && (
        <ChangePasswordModal 
          show={showChangePassword} 
          onClose={() => setShowChangePassword(false)} 
          onSubmit={handlePasswordChange} 
        />
      )}
      {showEventDetails && <EventDetailsModal />}
      {showBooking && <BookingModal />}
      {showChat && <ChatModal />}
      
      {/* User Profile Modals */}
      {showUserProfile && (
        <UserProfileModal 
          show={showUserProfile} 
          onClose={() => setShowUserProfile(false)}
          userProfile={selectedUserProfile}
          isOwnProfile={false}
        />
      )}
      
      {showOwnProfile && (
        <UserProfileModal 
          show={showOwnProfile} 
          onClose={() => setShowOwnProfile(false)}
          userProfile={selectedUserProfile}
          isOwnProfile={true}
          onEdit={() => {
            setShowOwnProfile(false);
            setShowEditOwnProfile(true);
          }}
        />
      )}

      {showEditOwnProfile && (
        <EditProfileModal 
          show={showEditOwnProfile} 
          onClose={() => setShowEditOwnProfile(false)}
          currentUser={currentUser}
          onSubmit={editUserProfile}
        />
      )}

      {/* Search and Creation Modals */}
      {showUserSearch && (
        <UserSearchModal 
          show={showUserSearch} 
          onClose={() => setShowUserSearch(false)}
          onSearch={searchUsers}
          searchResults={searchResults}
          onViewProfile={viewUserProfile}
        />
      )}

      {showCreateEvent && (
        <CreateEventModal 
          show={showCreateEvent} 
          onClose={() => setShowCreateEvent(false)}
          onSubmit={handleCreateEvent}
          userRole={currentUser?.ruolo}
        />
      )}

      {showEditEvent && (
        <EditEventModal 
          show={showEditEvent} 
          onClose={() => setShowEditEvent(false)}
          event={selectedEventToEdit}
          onSubmit={updateEvent}
        />
      )}

      {showCreateOrganization && (
        <CreateOrganizationModal 
          show={showCreateOrganization} 
          onClose={() => setShowCreateOrganization(false)}
          onSubmit={createOrganization}
        />
      )}

      {showCreateCapoPromoter && (
        <CreateCapoPromoterModal 
          show={showCreateCapoPromoter} 
          onClose={() => setShowCreateCapoPromoter(false)}
          onSubmit={createCapoPromoter}
          organizations={organizations}
        />
      )}

      {showCreatePromoter && (
        <CreatePromoterModal 
          show={showCreatePromoter} 
          onClose={() => setShowCreatePromoter(false)}
          onSubmit={createPromoter}
        />
      )}

      {showOrganizationDetails && (
        <OrganizationDetailsModal 
          show={showOrganizationDetails} 
          onClose={() => setShowOrganizationDetails(false)}
          organization={selectedOrganization}
          onViewProfile={viewUserProfile}
        />
      )}

      {showEditOrganization && (
        <EditOrganizationModal 
          show={showEditOrganization} 
          onClose={() => setShowEditOrganization(false)}
          organization={selectedOrganization}
          availableCapoPromoters={availableCapoPromoters}
          onSubmit={editOrganization}
        />
      )}
    </div>
  );
}

export default App;