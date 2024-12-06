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
  let difficultyLevel = prompt('Input difficulty level (e / n / h): ');
  console.log(difficultyLevel)
  // kysy vaikeustasoa kunnes pelaaja antaa oikean kirjaimen
  while (!['e', 'n', 'h'].includes(difficultyLevel)) {
    difficultyLevel = prompt('Input difficulty level (e / n / h): ');
    console.log(difficultyLevel)
  }
  // tästä ylöspäin kaikki formiin
  
  const response = await fetch(newGameUrl + `/${playerName}` + `/${difficultyLevel}`);
  if (!response.ok) throw new Error('Invalid server input!');
  const gameData = await response.json();
  gameSetup(gameData);
}

// jatka olemassa olevaa peliä
async function continueExistingGame() {
  const gameId = parseInt(prompt('Input game id: '));
  console.log(gameId);
  if (isNaN(gameId)) {
    return console.log('Invalid game id input');
  }
  
  const response = await fetch(gameInfoUrl + `/${gameId}`);
  if (!response.ok) throw new Error('Invalid server input!');
  const gameData = await response.json();
  gameSetup(gameData);
}

function gameSetup(gameData){
  //const gameData = await startNewGame();
  console.log(gameData);
  gameId = gameData.game_info.id;

  updateStatus(gameData);
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
  const flightInfoMarkerPopup = document.createElement('div');
  flightInfoMarkerPopup.classList.add('flight-info-marker')

  // lentoinfo
  const h4 = document.createElement('h4');
  h4.innerHTML = airportInfo.name;
  flightInfoMarkerPopup.append(h4);

  let distanceElem = document.createElement('p');
  distanceElem.innerHTML = `Distance ${airportInfo.flight_info.distance} km`;
  flightInfoMarkerPopup.append(distanceElem);

  let ticketCostElem = document.createElement('p');
  ticketCostElem.innerHTML = `Ticket cost ${airportInfo.flight_info.ticket_cost} €`;
  flightInfoMarkerPopup.append(ticketCostElem);

  let co2Elem = document.createElement('p');
  co2Elem.innerHTML = `CO2 consumption ${airportInfo.flight_info.co2_consumption} kg`;
  flightInfoMarkerPopup.append(co2Elem);

  // lentonappi
  const flyButton = document.createElement('button');
  flyButton.classList.add('button');
  flyButton.innerHTML = 'Fly';
  
  // mahdollistaa napin keskittämisen
  const flyButtonContainer = document.createElement('div');
  flyButtonContainer.append(flyButton)
  flightInfoMarkerPopup.append(flyButtonContainer);

  marker.bindPopup(flightInfoMarkerPopup);

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

// voit käyttä testaukseen, ei tee uutta peliä
continueExistingGame();


// Peliloop (kutsuu muita funktioita)

// aloita peli
document.querySelector("#start").addEventListener('click', startNewGame);

/*
while (stillPlaying) {


} else {
  lopeta peli
}
*/