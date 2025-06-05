import React, { useState } from 'react';

// User Profile Modal
export const UserProfileModal = ({ show, onClose, userProfile }) => {
  if (!show || !userProfile) return null;

  const getRoleIcon = (role) => {
    switch(role) {
      case 'clubly_founder': return '👑';
      case 'capo_promoter': return '🎯';
      case 'promoter': return '🎪';
      case 'cliente': return '🎉';
      default: return '👤';
    }
  };

  const getRoleName = (role) => {
    switch(role) {
      case 'clubly_founder': return 'Clubly Founder';
      case 'capo_promoter': return 'Capo Promoter';
      case 'promoter': return 'Promoter';
      case 'cliente': return 'Cliente';
      default: return 'Utente';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-2xl w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">👤 Profilo Utente</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-6">
            {/* Profile Image */}
            <div className="flex-shrink-0">
              {userProfile.profile_image ? (
                <img 
                  src={userProfile.profile_image} 
                  alt={`${userProfile.nome} ${userProfile.cognome}`}
                  className="w-32 h-32 rounded-full object-cover border-4 border-purple-500"
                />
              ) : (
                <div className="w-32 h-32 bg-gradient-to-br from-purple-600 to-purple-700 rounded-full flex items-center justify-center border-4 border-purple-500">
                  <span className="text-white font-bold text-4xl">
                    {userProfile.nome?.charAt(0)?.toUpperCase() || '?'}
                  </span>
                </div>
              )}
            </div>
            
            {/* User Information */}
            <div className="flex-1 space-y-4 text-center md:text-left">
              <div>
                <h3 className="text-white text-2xl font-bold">
                  {userProfile.nome} {userProfile.cognome}
                </h3>
                <p className="text-purple-400 text-lg font-semibold">
                  @{userProfile.username}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Ruolo</p>
                  <p className="text-white font-semibold flex items-center space-x-2">
                    <span>{getRoleIcon(userProfile.ruolo)}</span>
                    <span>{getRoleName(userProfile.ruolo)}</span>
                  </p>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Città</p>
                  <p className="text-white font-semibold">📍 {userProfile.citta}</p>
                </div>
                
                {userProfile.organization && (
                  <div className="bg-gray-800 rounded-lg p-3 md:col-span-2">
                    <p className="text-gray-400 text-sm">Organizzazione</p>
                    <p className="text-white font-semibold">🏢 {userProfile.organization}</p>
                  </div>
                )}
                
                <div className="bg-gray-800 rounded-lg p-3 md:col-span-2">
                  <p className="text-gray-400 text-sm">Membro da</p>
                  <p className="text-white font-semibold">
                    📅 {new Date(userProfile.created_at).toLocaleDateString('it-IT', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
              
              {userProfile.biografia && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Biografia</p>
                  <p className="text-gray-300 leading-relaxed">{userProfile.biografia}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// User Search Modal
export const UserSearchModal = ({ show, onClose, onSearch, searchResults, onViewProfile }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const handleSearch = () => {
    const searchParams = {
      search_term: searchTerm,
      role_filter: roleFilter || null,
      creation_date_from: dateFrom || null,
      creation_date_to: dateTo || null
    };
    onSearch(searchParams);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-purple-600 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🔍 Ricerca Utenti Clubly</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-purple-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Search Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <input
              type="text"
              placeholder="Cerca per nome, cognome o username..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
            
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            >
              <option value="">Tutti i ruoli</option>
              <option value="cliente">🎉 Cliente</option>
              <option value="promoter">🎪 Promoter</option>
              <option value="capo_promoter">🎯 Capo Promoter</option>
              <option value="clubly_founder">👑 Clubly Founder</option>
            </select>
            
            <input
              type="date"
              placeholder="Data inizio"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
            
            <input
              type="date"
              placeholder="Data fine"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
          </div>
          
          <button 
            onClick={handleSearch}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-bold transition-colors mb-6"
          >
            🔍 Cerca
          </button>
          
          {/* Search Results */}
          <div className="space-y-4">
            <h3 className="text-white text-xl font-bold">Risultati ({searchResults.length})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map(user => (
                <div 
                  key={user.id}
                  onClick={() => onViewProfile(user.id)}
                  className="bg-gray-800 rounded-lg p-4 cursor-pointer hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    {user.profile_image ? (
                      <img 
                        src={user.profile_image} 
                        alt={user.nome}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{user.nome?.charAt(0)}</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="text-white font-bold">@{user.username}</p>
                      <p className="text-gray-300 text-sm">{user.nome} {user.cognome}</p>
                      <p className="text-gray-400 text-xs">
                        {user.ruolo === 'clubly_founder' ? '👑' : 
                         user.ruolo === 'capo_promoter' ? '🎯' :
                         user.ruolo === 'promoter' ? '🎪' : '🎉'} {user.citta}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {searchResults.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <p>Nessun utente trovato</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Create Event Modal
export const CreateEventModal = ({ show, onClose, onSubmit, userRole }) => {
  const [eventData, setEventData] = useState({
    name: '',
    date: '',
    start_time: '',
    location: '',
    organization: '',
    end_time: '',
    lineup: '',
    location_address: '',
    total_tables: '',
    table_types: '',
    max_party_size: '10'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const formattedData = {
      ...eventData,
      lineup: eventData.lineup ? eventData.lineup.split(',').map(dj => dj.trim()) : [],
      table_types: eventData.table_types ? eventData.table_types.split(',').map(type => type.trim()) : [],
      total_tables: parseInt(eventData.total_tables) || 0,
      max_party_size: parseInt(eventData.max_party_size) || 10
    };
    onSubmit(formattedData, userRole);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-red-600 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🎉 Crea Nuovo Evento</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-red-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Required Fields */}
              <div className="col-span-full">
                <label className="text-red-400 font-bold block mb-2">📝 Campi Obbligatori</label>
              </div>
              
              <input
                type="text"
                placeholder="Nome dell'evento *"
                value={eventData.name}
                onChange={(e) => setEventData({...eventData, name: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <input
                type="date"
                value={eventData.date}
                onChange={(e) => setEventData({...eventData, date: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              <select
                value={eventData.start_time}
                onChange={(e) => setEventData({...eventData, start_time: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              >
                <option value="">Orario di inizio *</option>
                <option value="18:00">18:00</option>
                <option value="19:00">19:00</option>
                <option value="20:00">20:00</option>
                <option value="21:00">21:00</option>
                <option value="22:00">22:00</option>
                <option value="22:30">22:30</option>
                <option value="23:00">23:00</option>
                <option value="23:30">23:30</option>
                <option value="00:00">00:00</option>
              </select>
              
              <input
                type="text"
                placeholder="Locale *"
                value={eventData.location}
                onChange={(e) => setEventData({...eventData, location: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all"
                required
              />
              
              {/* Optional Fields */}
              <div className="col-span-full mt-6">
                <label className="text-blue-400 font-bold block mb-2">⭐ Campi Facoltativi</label>
              </div>
              
              <input
                type="text"
                placeholder="Organizzazione"
                value={eventData.organization}
                onChange={(e) => setEventData({...eventData, organization: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <select
                value={eventData.end_time}
                onChange={(e) => setEventData({...eventData, end_time: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              >
                <option value="">Orario di fine</option>
                <option value="01:00">01:00</option>
                <option value="02:00">02:00</option>
                <option value="03:00">03:00</option>
                <option value="04:00">04:00</option>
                <option value="05:00">05:00</option>
                <option value="06:00">06:00</option>
              </select>
              
              <input
                type="text"
                placeholder="Line-up DJ (separati da virgola)"
                value={eventData.lineup}
                onChange={(e) => setEventData({...eventData, lineup: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <input
                type="text"
                placeholder="Indirizzo del locale"
                value={eventData.location_address}
                onChange={(e) => setEventData({...eventData, location_address: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <input
                type="number"
                placeholder="Numero tavoli disponibili"
                value={eventData.total_tables}
                onChange={(e) => setEventData({...eventData, total_tables: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                min="0"
              />
              
              <input
                type="text"
                placeholder="Tipi di tavoli (separati da virgola)"
                value={eventData.table_types}
                onChange={(e) => setEventData({...eventData, table_types: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              />
              
              <input
                type="number"
                placeholder="Max persone per tavolo"
                value={eventData.max_party_size}
                onChange={(e) => setEventData({...eventData, max_party_size: e.target.value})}
                className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                min="1"
                max="20"
              />
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🎉 Crea Evento
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Create Organization Modal
export const CreateOrganizationModal = ({ show, onClose, onSubmit }) => {
  const [orgData, setOrgData] = useState({
    name: '',
    location: '',
    capo_promoter_username: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(orgData);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🏢 Crea Organizzazione</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nome organizzazione"
              value={orgData.name}
              onChange={(e) => setOrgData({...orgData, name: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="text"
              placeholder="Città"
              value={orgData.location}
              onChange={(e) => setOrgData({...orgData, location: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="text"
              placeholder="Username capo promoter"
              value={orgData.capo_promoter_username}
              onChange={(e) => setOrgData({...orgData, capo_promoter_username: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
              required
            />
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🏢 Crea Organizzazione
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Create Capo Promoter Modal
export const CreateCapoPromoterModal = ({ show, onClose, onSubmit }) => {
  const [userData, setUserData] = useState({
    nome: '',
    email: '',
    organization: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(userData);
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-green-600 rounded-xl max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🎯 Crea Capo Promoter</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-green-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              placeholder="Nome"
              value={userData.nome}
              onChange={(e) => setUserData({...userData, nome: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="email"
              placeholder="Email"
              value={userData.email}
              onChange={(e) => setUserData({...userData, email: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
              required
            />
            
            <input
              type="text"
              placeholder="Organizzazione (opzionale)"
              value={userData.organization}
              onChange={(e) => setUserData({...userData, organization: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all"
            />
            
            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-3">
              <p className="text-yellow-400 text-sm">
                ⚠️ Verrà generata una password temporanea che l'utente dovrà cambiare al primo accesso.
              </p>
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              🎯 Crea Capo Promoter
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Organization Details Modal
export const OrganizationDetailsModal = ({ show, onClose, organization, onViewProfile }) => {
  if (!show || !organization) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-blue-600 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">🏢 {organization.name}</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-blue-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Organization Info */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-blue-400 font-bold text-xl mb-4">📍 Informazioni</h3>
              <div className="space-y-3">
                <p className="text-gray-300"><span className="text-gray-400">Nome:</span> {organization.name}</p>
                <p className="text-gray-300"><span className="text-gray-400">Città:</span> {organization.location}</p>
                <p className="text-gray-300"><span className="text-gray-400">Membri:</span> {organization.members?.length || 0}</p>
                <p className="text-gray-300"><span className="text-gray-400">Eventi:</span> {organization.events?.length || 0}</p>
                <p className="text-gray-300">
                  <span className="text-gray-400">Creata il:</span> {' '}
                  {new Date(organization.created_at).toLocaleDateString('it-IT')}
                </p>
              </div>
            </div>
            
            {/* Members */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-green-400 font-bold text-xl mb-4">👥 Membri ({organization.members?.length || 0})</h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {organization.members?.map(member => (
                  <div 
                    key={member.id}
                    onClick={() => onViewProfile(member.id)}
                    className="flex items-center space-x-3 bg-gray-700 rounded-lg p-3 cursor-pointer hover:bg-gray-600 transition-colors"
                  >
                    {member.profile_image ? (
                      <img 
                        src={member.profile_image} 
                        alt={member.nome}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold">{member.nome?.charAt(0)}</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="text-white font-bold">@{member.username}</p>
                      <p className="text-gray-300 text-sm">{member.nome} {member.cognome}</p>
                      <p className="text-gray-400 text-xs">
                        {member.ruolo === 'capo_promoter' ? '🎯 Capo Promoter' : '🎪 Promoter'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Events */}
          <div className="mt-6 bg-gray-800 rounded-lg p-6">
            <h3 className="text-red-400 font-bold text-xl mb-4">🎉 Eventi ({organization.events?.length || 0})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {organization.events?.map(event => (
                <div key={event.id} className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white font-bold">{event.name}</h4>
                  <p className="text-gray-300 text-sm">📅 {event.date}</p>
                  <p className="text-gray-300 text-sm">📍 {event.location}</p>
                  <p className="text-gray-300 text-sm">🕘 {event.start_time}</p>
                </div>
              ))}
            </div>
            
            {organization.events?.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <p>Nessun evento trovato per questa organizzazione</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Edit Event Modal for Capo Promoter
export const EditEventModal = ({ show, onClose, event, onSubmit }) => {
  const [eventData, setEventData] = useState({
    name: '',
    lineup: '',
    start_time: '',
    end_time: '',
    guests: ''
  });

  // Initialize form data when event changes
  React.useEffect(() => {
    if (event) {
      setEventData({
        name: event.name || '',
        lineup: Array.isArray(event.lineup) ? event.lineup.join(', ') : (event.lineup || ''),
        start_time: event.start_time || '',
        end_time: event.end_time || '',
        guests: Array.isArray(event.guests) ? event.guests.join(', ') : (event.guests || '')
      });
    }
  }, [event]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const formattedData = {
      name: eventData.name,
      lineup: eventData.lineup ? eventData.lineup.split(',').map(dj => dj.trim()) : [],
      start_time: eventData.start_time,
      end_time: eventData.end_time,
      guests: eventData.guests ? eventData.guests.split(',').map(guest => guest.trim()) : []
    };
    onSubmit(event.id, formattedData);
  };

  if (!show || !event) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-orange-600 rounded-xl max-w-2xl w-full shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-white text-2xl font-bold">✏️ Modifica Evento</h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-orange-400 text-2xl font-bold transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Event Info */}
          <div className="bg-gray-800 rounded-lg p-4 mb-6">
            <h3 className="text-orange-400 font-bold mb-2">📋 Informazioni Evento</h3>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Data:</span> {event.date}</p>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Locale:</span> {event.location}</p>
            <p className="text-gray-300 text-sm"><span className="text-gray-400">Organizzazione:</span> {event.organization}</p>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 mb-6">
            <h4 className="text-yellow-400 font-bold text-sm mb-2">⚠️ Permessi di Modifica</h4>
            <p className="text-yellow-300 text-xs">
              Come Capo Promoter puoi modificare: <strong>Nome evento, Orario di inizio, Orario di fine, Line-up DJ e Guest</strong>
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-4">
              <div>
                <label className="text-orange-400 font-bold block mb-2">📝 Nome Evento</label>
                <input
                  type="text"
                  placeholder="Nome dell'evento"
                  value={eventData.name}
                  onChange={(e) => setEventData({...eventData, name: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  required
                />
              </div>

              <div>
                <label className="text-orange-400 font-bold block mb-2">🎵 Line-up DJ</label>
                <input
                  type="text"
                  placeholder="DJ set (separati da virgola)"
                  value={eventData.lineup}
                  onChange={(e) => setEventData({...eventData, lineup: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                />
                <p className="text-gray-400 text-xs mt-1">Esempio: DJ Marco, DJ Sara, DJ Alex</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-orange-400 font-bold block mb-2">🕘 Orario di Inizio</label>
                  <select
                    value={eventData.start_time}
                    onChange={(e) => setEventData({...eventData, start_time: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                    required
                  >
                    <option value="">Seleziona orario</option>
                    <option value="18:00">18:00</option>
                    <option value="19:00">19:00</option>
                    <option value="20:00">20:00</option>
                    <option value="21:00">21:00</option>
                    <option value="22:00">22:00</option>
                    <option value="22:30">22:30</option>
                    <option value="23:00">23:00</option>
                    <option value="23:30">23:30</option>
                    <option value="00:00">00:00</option>
                    <option value="01:00">01:00</option>
                  </select>
                </div>

                <div>
                  <label className="text-orange-400 font-bold block mb-2">🕘 Orario di Fine</label>
                  <select
                    value={eventData.end_time}
                    onChange={(e) => setEventData({...eventData, end_time: e.target.value})}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                  >
                    <option value="">Seleziona orario fine</option>
                    <option value="01:00">01:00</option>
                    <option value="02:00">02:00</option>
                    <option value="03:00">03:00</option>
                    <option value="04:00">04:00</option>
                    <option value="05:00">05:00</option>
                    <option value="06:00">06:00</option>
                    <option value="07:00">07:00</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-orange-400 font-bold block mb-2">⭐ Guest Speciali</label>
                <input
                  type="text"
                  placeholder="Guest speciali (separati da virgola)"
                  value={eventData.guests}
                  onChange={(e) => setEventData({...eventData, guests: e.target.value})}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 outline-none transition-all"
                />
                <p className="text-gray-400 text-xs mt-1">Esempio: Artista Speciale, Celebrity Guest</p>
              </div>
            </div>
            
            <div className="flex space-x-4 pt-4">
              <button 
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg font-bold transition-colors"
              >
                Annulla
              </button>
              <button 
                type="submit" 
                className="flex-1 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white py-3 rounded-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                💾 Salva Modifiche
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};