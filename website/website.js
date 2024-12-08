'use strict';

// scrollaa loppuun

const map = L.map('map', {tap: false});
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);

const airportMarkers = L.featureGroup().addTo(map);

/*
//Jos haluamme, voimme lisätä openstreetmapin googlemapin sijaan.
const map = L.map('map').setView([60.23, 24.74], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
//const airportMarkers = L.featureGroup().addTo(map);
*/

const apiUrl = 'http://127.0.0.1:5000/';
const newGameUrl = apiUrl + '/new-game';
const gameInfoUrl = apiUrl + '/game-info';
const flyToUrl = apiUrl + '/fly-to';

let gameId;
let stillPlaying = true;

// aloita uusi peli
async function startNewGame() {
  // kysyy nimen
  document.querySelector('#player-modal').classList.remove('hide');

  var playerName = await new Promise(function(resolve) {
    document.querySelector('#player-form').addEventListener('submit', function(evt) {
      evt.preventDefault();
      var playerName = document.querySelector('#player-input').value;
      document.querySelector('#player-modal').classList.add('hide');
      resolve(playerName);
    });
  });

  // kysyy vaikeustason
  document.querySelector('#difficulty-modal').classList.remove('hide');

  var difficultyLevel = await new Promise(function(resolve) {
    var buttons = document.querySelectorAll('#difficulty-form input[type="button"]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', function() {
        var difficultyLevel = this.value.toLowerCase();
        console.log('Selected difficulty level: ' + difficultyLevel);
        document.querySelector('#difficulty-modal').classList.add('hide');
        resolve(difficultyLevel);
      });
    }
  });

  var response = await fetch(newGameUrl + '/' + playerName + '/' + difficultyLevel);
  if (!response.ok) throw new Error('Invalid server input!');
  var gameData = await response.json();
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
  gameId = gameData.game_info.id;
  updateStatus(gameData);
}

// päivittää pelin tiedot käyttöliittymään
function updateStatus(data) {
  console.log(data);
  
  // pelaajan tiedot
  document.querySelector('#player').innerHTML = `${data.game_info.screen_name}`;
  document.querySelector('#money').innerHTML = `${data.game_info.money}`;
  document.querySelector('#location').innerHTML = `${data.current_location_info.name}`;
  document.querySelector('#co2').innerHTML = `${data.game_info.co2_consumed}`;
  document.querySelector('#clue').innerHTML = `${data.game_info.clue}`;

  // tyhjentää kartan merkeistä
  airportMarkers.clearLayers();

  // kartan zoom. zoomaa lähemmäs jos aarremaassa
  let zoomLevel = 4;
  if (data.game_info.in_treasure_land) zoomLevel = 5;
  // to do: älä muuta zoomia pelin aikana (jätä pelaajan asettama zoom)
  // nyt zoom hyppii matkustaessa mikä on häiritsevää

  // nykyisen sijainnin marker
  let marker = L.marker([
    data.current_location_info.latitude, data.current_location_info.longitude]).addTo(map);
    airportMarkers.addLayer(marker);
    map.setView([data.current_location_info.latitude, data.current_location_info.longitude], zoomLevel);
    
  // onko pelaaja aarremaassa, jos on näytetään maan nimi lentokentän lisäksi
  const inTreasureLand = data.game_info.in_treasure_land;

  // kaikkien kenttien markerit kartalle
  for (let airportInfo of data.available_airports_info) {
    let airportMarker = L.marker([airportInfo.latitude, airportInfo.longitude], {
      icon: L.divIcon({
        className: 'custom-marker',
        html: '<div class="marker-icon"></div>',
        iconSize: [25, 25],
      })
    }).addTo(map);
    airportMarkers.addLayer(airportMarker);
    addFlightInfoToMarker(airportInfo, airportMarker, inTreasureLand);

    // markereille eri värit riippuen voiko kentälle matkustaa ja onko vierailtu
    if (airportInfo.flight_info.can_fly_to && airportInfo.visited === 0) {
       airportMarker._icon.classList.add('marker-green');

    } else if (airportInfo.flight_info.can_fly_to && airportInfo.visited === 1) {
       airportMarker._icon.classList.add('marker-darkgreen');

    } else if (!airportInfo.flight_info.can_fly_to && airportInfo.visited === 0) {
       airportMarker._icon.classList.add('marker-red');

    } else if (!airportInfo.flight_info.can_fly_to && airportInfo.visited === 1) {
      airportMarker._icon.classList.add('marker-darkred');
    }
  }
}

// lentoinfo markerille ja lentonappi
function addFlightInfoToMarker(airportInfo, marker, inTreasureLand) {
  const flightInfoMarkerPopup = document.createElement('div');
  flightInfoMarkerPopup.classList.add('flight-info-marker');
  
  // lentoinfo
  // näytä maan nimi kansainvälisillä lennoilla ja kentän nimi kotimaisilla lennoilla
  const h4 = document.createElement('h4');
  let airportNameDisplay = airportInfo.name;
  if (!inTreasureLand) {
    airportNameDisplay = `${airportInfo.country_name}`;
  }
  h4.innerHTML = airportNameDisplay;
  flightInfoMarkerPopup.append(h4);
  
  // etäisyys
  let distanceElem = document.createElement('p');
  distanceElem.innerHTML = `Distance ${airportInfo.flight_info.distance} km`;
  flightInfoMarkerPopup.append(distanceElem);
  
  // lipun hinta
  let ticketCostElem = document.createElement('p');
  ticketCostElem.innerHTML = `Ticket cost ${airportInfo.flight_info.ticket_cost} €`;
  flightInfoMarkerPopup.append(ticketCostElem);
  
  // co2 kulutus
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

    // testaa onko wise man, jos on niin kyselyt
    wiseManQuestion(data);

    // testaa onko kentällä käyty, jos ei ole kerro advice
    if (!airportInfo.visited) {
      adviceGuy(data);
    }
  });
}

// advice guy funktiot

// testaa onko advice guy (mahdollistaa tällä hetkellä neuvon saamisen uudelleen)
function hasUnVisitedAdviceGuy(data) {
  // ehdon pitäisi olla: if (data.current_location_info.advice_guy && data.current_location_info.visited === 0)
  if (data.current_location_info.advice_guy) {
    console.log('Advice guy found!');
    return true;
  } else {
    console.log('No advice guy here.')
    return false;
  }
}

// advice guy antaa neuvon
function adviceGuy(data) {
  if (hasUnVisitedAdviceGuy(data)) {
    alert(`You encounter advice guy! Advice: ${data.current_location_info.advice_guy.advice}`);
  }
}

// wise man funktioiden alku

// testaa onko wise man, johon ei ole vastattu
function hasUnansweredWiseMan(data) {
  if (data.current_location_info.wise_man && data.current_location_info.wise_man.answered === 0) {
  console.log("Wise man on, ei ole vastattu!");
  return true;
  } else {
    console.log("No wise man data found.");
    return false;
  }
}

// wise man kysyy kysymyksen (tämä ei vielä päivitä answered-kohtaa)
function wiseManQuestion(data) {
  if (hasUnansweredWiseMan(data)) {
    const userAnswer = prompt(`You encounter a wise man! Question: ${data.current_location_info.wise_man.wise_man_question}. Input a, b or c.`);
    if (userAnswer === data.current_location_info.wise_man.answer) {
      console.log('Correct!')
      // anna rahaa, päivitä answered-kohdaksi 1 - fetch wise-man/game id/is correct answer?
    } else {
      console.log('Wrong answer.')
    }

  }
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
  //lopeta peli
  alert('Out of money! Game over!');
}
*/

// popupit

function openPopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.style.display = 'block';
}

function closePopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.style.display = 'none';
}

var btn1 = document.getElementById('open-wise-man-modal-popup');
var btn2 = document.getElementById('open-advice-guy-modal-popup');
var btn3 = document.getElementById('open-victory-modal-popup');
var btn4 = document.getElementById('open-defeat-modal-popup');
var btn5 = document.getElementById('open-yes-or-no-popup');

var closeButtons = document.getElementsByClassName('close');

btn1.onclick = function() {
  openPopup('wise-man-modal');
};

btn2.onclick = function() {
  openPopup('advice-guy-modal');
};

btn3.onclick = function() {
  openPopup('victory-modal');
};

btn4.onclick = function() {
  openPopup('defeat-modal');
};

btn5.onclick = function() {
  openPopup('yes-or-no-modal');
};

for (var i = 0; i < closeButtons.length; i++) {
  closeButtons[i].onclick = function() {
    var popupId = this.getAttribute('data-popup');
    closePopup(popupId);
  };
}

