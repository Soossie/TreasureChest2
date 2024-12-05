'use strict';

// scrollaa loppuun

const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
//map.setView([60, 24], 7);

const airportMarkers = L.featureGroup().addTo(map);

//let marker = L.marker([60.3172, 24.963]).addTo(map); // esimerkki marker

/*
//Jos haluamme, voimme lisätä openstreetmapin googlemapin sijaan.
const map = L.map('map').setView([60.23, 24.74], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
let marker = L.marker([60.3172, 24.963]).addTo(map);
 */

const apiUrl = 'http://127.0.0.1:3000/';
const newGameUrl = apiUrl + '/new-game';
const gameInfoUrl = apiUrl + '/game-info';
const flyToUrl = apiUrl + '/fly-to';

let gameId;
let stillPlaying = true;

// aloita uusi peli
async function startNewGame() {
  // muuta prompt formiksi
  const playerName = prompt('Input name: ');
  const difficultyLevel = prompt('Input difficulty level (e / n / h): ');
  
  const response = await fetch(newGameUrl + `/${playerName}` + `/${difficultyLevel}`);
  if (!response.ok) throw new Error('Invalid server input!');
  const gameData = await response.json();
  gameSetup(gameData);
}

async function gameSetup(gameData){
  //const gameData = await startNewGame();
  console.log(gameData);
  gameId = gameData.game_info.id;
  
  updateStatus(gameData);
}

async function getGameInfo() {
  const gameId = prompt('Input game id: ')
  
  const response = await fetch(gameInfoUrl + `/${gameId}`);
  if (!response.ok) throw new Error('Invalid server input!');
  return await response.json();
}

async function guiSetup(){
  const gameData = await getGameInfo();
  console.log(gameData);
  updateStatus(gameData);
  gameId = gameData.game_info.id;
}

// päivittää pelin tiedot käyttöliittymään
function updateStatus(data) {
  // pelaajan tiedot
  document.querySelector('#player').innerHTML = `${data.game_info.screen_name}`;
  document.querySelector('#money').innerHTML = `${data.game_info.money}`;
  document.querySelector('#location').innerHTML = `${data.current_location_info.name}`;
  document.querySelector('#co2').innerHTML = `${data.game_info.co2_consumed}`;
  document.querySelector('#clue').innerHTML = `${data.game_info.clue}`;
  
  // tyhjentää kartan merkeistä
  airportMarkers.clearLayers();
  
  // karttamerkit
  let marker = L.marker([data.current_location_info.latitude, data.current_location_info.longitude]).addTo(map);
  map.setView([data.current_location_info.latitude, data.current_location_info.longitude], 4);
  
  // lisää kaikille lentokentille seuraavat kolme riviä:
  const airport_info = data.available_airports_info[0];  // testiarvo: valitsee aina ensimmäisen kentän
  airportMarkers.addLayer(marker);
  addFlightInfoToMarker(airport_info, marker);
  
  // lisää kaikki lentokentät tähän. löytyy datasta kohdasta available_airports_info. muuta eri värisiksi
  
}

// lentoinfo markerille ja lentonappi
function addFlightInfoToMarker(airportInfo, marker) {
  const flighInfoMarkerPopup = document.createElement('div');
  flighInfoMarkerPopup.classList.add('flight-info-marker')
  
  // lentoinfo
  const h4 = document.createElement('h4');
  h4.innerHTML = airportInfo.name;
  flighInfoMarkerPopup.append(h4);
  
  let distanceElem = document.createElement('p');
  distanceElem.innerHTML = `Distance ${airportInfo.flight_info.distance} km`;
  flighInfoMarkerPopup.append(distanceElem);
  
  let ticketCostElem = document.createElement('p');
  ticketCostElem.innerHTML = `Ticket cost ${airportInfo.flight_info.ticket_cost} €`;
  flighInfoMarkerPopup.append(ticketCostElem);
  
  let co2Elem = document.createElement('p');
  co2Elem.innerHTML = `Co2 consumption ${airportInfo.flight_info.co2_consumption} kg`;
  flighInfoMarkerPopup.append(co2Elem);
  
  // lentonappi
  const flyButton = document.createElement('button');
  flyButton.classList.add('button');
  flyButton.innerHTML = 'Fly here';
  //flighInfoMarkerPopup.append(flyButton);
  
  const flyButtonContainer = document.createElement('div');
  flyButtonContainer.append(flyButton)
  flighInfoMarkerPopup.append(flyButtonContainer);
  
  marker.bindPopup(flighInfoMarkerPopup);
  
  // event napille
  flyButton.addEventListener('click', async function () {
    const response = await fetch(flyToUrl + `/${gameId}/${airportInfo.icao}`);
    if (!response.ok) {
      throw new Error('Invalid server input!');
    }
    const data = await response.json();
    updateStatus(data);
  });
}


// valitse näistä yksi:

// tekee uuden pelin
//gameSetup(apiUrl);

// voit käyttä testaukseen guiSetup, ei tee uutta peliä
guiSetup();


// Peliloop (kutsuu muita funktioita)

// aloita peli
document.querySelector("#start").addEventListener('click', startNewGame);

/*
while (stillPlaying) {


}
*/