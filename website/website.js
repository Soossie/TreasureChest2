'use strict';

// scrollaa loppuun

const map = L.map('map', {tap: false});
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);

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
  console.log(difficultyLevel);
  // kysy vaikeustasoa kunnes pelaaja antaa oikean kirjaimen
  while (!['e', 'n', 'h'].includes(difficultyLevel)) {
    difficultyLevel = prompt('Input difficulty level (e / n / h): ');
    console.log(difficultyLevel);
  }


// tästä ylöspäin kaikki formiin

  /* tämä kesken, pitää saada nimi ja vaikeustaso käyttöön funktioiden jälkeen, resolve?
async function startNewGame() {
  document.querySelector('#player-modal').classList.remove('hide');
  document.querySelector('#player-form').addEventListener('submit', function(evt) {
        evt.preventDefault();

        // kysyy nimen formilla
        var playerName = document.querySelector('#player-input').value;
        document.querySelector('#player-modal').classList.add('hide');

        // vaikeustaso
        document.querySelector('#difficulty-modal').classList.remove('hide');

        var difficultyLevel = '';

        var buttons = document.querySelectorAll(
            '#difficulty-form input[type="button"]');
        for (var i = 0; i < buttons.length; i++) {
          buttons[i].addEventListener('click', function() {
            difficultyLevel = this.value.toLowerCase();
            console.log('Selected difficulty level: ' + difficultyLevel);
          });
        }

      });
*/

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

function gameSetup(gameData) {
  //const gameData = await startNewGame();
  console.log(gameData);
  gameId = gameData.game_info.id;

  updateStatus(gameData);
}

// päivittää pelin tiedot käyttöliittymään
function updateStatus(data) {
  // pelaajan tiedot
  document.querySelector(
      '#player').innerHTML = `${data.game_info.screen_name}`;
  document.querySelector('#money').innerHTML = `${data.game_info.money}`;
  document.querySelector(
      '#location').innerHTML = `${data.current_location_info.name}`;
  document.querySelector('#co2').innerHTML = `${data.game_info.co2_consumed}`;
  document.querySelector('#clue').innerHTML = `${data.game_info.clue}`;

  // tyhjentää kartan merkeistä
  airportMarkers.clearLayers();

  // karttamerkit
  //const blueIcon = L.divIcon({className:'blue_icon'})
  //const greenIcon = L.divIcon({className:'green_icon'})
  //const darkgreenIcon = L.divIcon({className:'darkgreen_icon'})
  //const redIcon = L.divIcon({className:'darkred_icon'})
  //const darkredIcon = L.divIcon({className:'blue_icon'})

  let marker = L.marker([
    data.current_location_info.latitude,
    data.current_location_info.longitude]).addTo(map);
  airportMarkers.addLayer(marker);
  map.setView([
    data.current_location_info.latitude,
    data.current_location_info.longitude], 4);

  //alku
  for (let airportInfo of data.available_airports_info) {
    let airportMarker = L.marker(
        [airportInfo.latitude, airportInfo.longitude]).
        addTo(map);
    airportMarkers.addLayer(airportMarker);
    addFlightInfoToMarker(airportInfo, airportMarker);

    // asettaa markereille eri värit riippuen voiko kentälle matkustaa ja onko vierailtu
    if (airportInfo.flight_info.can_fly_to && airportInfo.visited === 0) {
      airportMarker._icon.style.filter = 'hue-rotate(260deg)';

    } else if (airportInfo.flight_info.can_fly_to && airportInfo.visited ===
        1) {
      airportMarker._icon.style.filter = 'hue-rotate(310deg)';

    } else if (!airportInfo.flight_info.can_fly_to && airportInfo.visited ===
        0) {
      airportMarker._icon.style.filter = 'hue-rotate(100deg)';

    } else if (!airportInfo.flight_info.can_fly_to && airportInfo.visited ===
        1) {
      airportMarker._icon.style.filter = 'hue-rotate(150deg)';
    }

  }

}

// lentoinfo markerille ja lentonappi
function addFlightInfoToMarker(airportInfo, marker) {
  const flightInfoMarkerPopup = document.createElement('div');
  flightInfoMarkerPopup.classList.add('flight-info-marker');

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
  flyButtonContainer.append(flyButton);
  flightInfoMarkerPopup.append(flyButtonContainer);

  marker.bindPopup(flightInfoMarkerPopup);

  // event napille
  flyButton.addEventListener('click', async function() {
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
document.querySelector('#start').addEventListener('click', startNewGame);

/*
while (stillPlaying) {

} else {
  lopeta peli
}
*/

// Function to open a popup
function openPopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.style.display = 'block';
}

// Function to close a popup
function closePopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.style.display = 'none';
}

// Get the buttons that open the popups
var btn1 = document.getElementById('open-wise-man-modal-popup');
var btn2 = document.getElementById('open-advice-guy-modal-popup');

// Get the <span> elements that close the popups
var closeButtons = document.getElementsByClassName('close');

// When the user clicks the button, open the corresponding popup
btn1.onclick = function() {
  openPopup('wise-man-modal');
};

btn2.onclick = function() {
  openPopup('advice-guy-modal');
};

// When the user clicks on <span> (x), close the corresponding popup
for (var i = 0; i < closeButtons.length; i++) {
  closeButtons[i].onclick = function() {
    var popupId = this.getAttribute('data-popup');
    closePopup(popupId);
  };
}

