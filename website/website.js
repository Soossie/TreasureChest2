'use strict';

const map = L.map('map', {tap: false});
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);

const airportMarkers = L.featureGroup().addTo(map);

const apiUrl = 'http://127.0.0.1:3000/';
const newGameUrl = apiUrl + '/new-game';
const gameInfoUrl = apiUrl + '/game-info';
const flyToUrl = apiUrl + '/fly-to';
const wiseManUrl = apiUrl + '/wise-man';

let gameId;
let gameData;
let co2AlertShown = false;
let treasureLandAlertShown = false;

// aloita uusi peli
async function startNewGame() {
  // nollaa treasureLandAlertShown
  treasureLandAlertShown = false;
  // muuttaa CO2-värin mustaksi
  document.querySelector('#co2').style.color = 'black';
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
        document.querySelector('#difficulty-modal').classList.add('hide');
        resolve(difficultyLevel);
      });
    }
  });

  var response = await fetch(newGameUrl + '/' + playerName + '/' + difficultyLevel);
  if (!response.ok) throw new Error('Invalid server input!');
  gameData = await response.json();
  gameSetup();

  // näytä story
  document.querySelector('#story-modal').classList.remove('hide');
}

// debuggaus
/*
// jatka olemassa olevaa peliä
async function continueExistingGame() {
  const gameId = parseInt(prompt('Input game id: '));
  console.log(gameId);
  if (isNaN(gameId)) {
    return console.log('Invalid game id input');
  }

  const response = await fetch(gameInfoUrl + `/${gameId}`);
  if (!response.ok) throw new Error('Invalid server input!');
  gameData = await response.json();
  gameSetup();
}
 */

// debug, ei tee uutta peliä
//continueExistingGame();

function gameSetup() {
  gameId = gameData.game_info.id;
  updateStatus(NaN);
}

// päivitä pelaajan tiedot
function updatePlayerInfoPanel() {
  document.querySelector('#player').innerHTML = `${gameData.game_info.screen_name}`;
  document.querySelector('#money').innerHTML = `${gameData.game_info.money} €`;
  document.querySelector('#location').innerHTML = `${gameData.current_location_info.name}`;
  document.querySelector('#co2').innerHTML = `${gameData.game_info.co2_consumed} kg`;
  document.querySelector('#clue').innerHTML = `${gameData.game_info.clue}`;
}

let userZoomLevel = 4;
map.on('zoomend', function () {
  userZoomLevel = map.getZoom();
});

// päivitä nykyinen sijainti kartalle
function updateCurrentLocationMarkerOnly() {
  // tyhjentää kartan merkeistä
  airportMarkers.clearLayers();

  // Käytä pelaajan asettamaa zoom-tasoa
  let zoomLevel = userZoomLevel !== null ? userZoomLevel : 4;
  map.setZoom(userZoomLevel);

  // nykyisen sijainnin marker
  let marker = L.marker([gameData.current_location_info.latitude, gameData.current_location_info.longitude]).addTo(map);
  airportMarkers.addLayer(marker);
  map.setView([gameData.current_location_info.latitude, gameData.current_location_info.longitude], zoomLevel);
}

// päivitä nykyinen sijainti ja kaikki lentokentät kartalle
function updateMapMarkers() {
  // nykyinen sijainti
  updateCurrentLocationMarkerOnly();

  // onko pelaaja aarremaassa, jos on näytetään maan nimi lentokentän lisäksi
  const inTreasureLand = gameData.game_info.in_treasure_land;

  // kaikkien kenttien markerit kartalle
  for (let airportInfo of gameData.available_airports_info) {
    let airportMarker = L.marker([airportInfo.latitude, airportInfo.longitude], {
      icon: L.divIcon({
        className: 'custom-marker',
        html: '<div class="marker-icon"></div>',
        iconSize: [12, 12],
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

// ohjelma odottaa x ms. odotuksen aikana nykyinen sijainti ehtii päivittyä kartalle,
// jolloin esim. mahdollisen tietäjän sattuessa kohdalle pelaajan kartta on keskittynyt uudelle sijainnille
function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

// päivittää pelin tiedot käyttöliittymään
async function updateStatus(visitedBefore=false) {
  console.log(gameData);
  updatePlayerInfoPanel();

  // odota x millisekuntia jotta nykyinen sijainti päivittyy kartalle
  updateCurrentLocationMarkerOnly();
  await delay(200);

  // tarkista onko pelaaja aarremaassa
  const inTreasureLand = gameData.game_info.in_treasure_land;
  if (inTreasureLand && !treasureLandAlertShown) {
    // näytä ilmoitus (yhden kerran)
    document.querySelector('#treasure-land-modal').classList.remove('hide');
    treasureLandAlertShown = true;

    // odota, että käyttäjä sulkee ilmoituksen
    await new Promise(function(resolve) {
      document.querySelector('#close-treasure-land').addEventListener('click', function () {
        document.querySelector('#treasure-land-modal').classList.add('hide');
        resolve();
      })
    })
  }

  // tarkista onko kentällä aarre
  if (gameData.current_location_info.has_treasure) {
    // wise man viimeinen kysymys
    finalWiseManQuestion();

  } else {
    if (gameData.current_location_info.wise_man) {  // wise man
      // testaa onko wise man, jos on niin kyselyt
      await wiseManQuestion();
      updatePlayerInfoPanel();

    } else if (gameData.current_location_info.advice_guy) {  // advice guy
      // testaa onko kentällä käyty, jos ei ole kerro vinkki
      if (!visitedBefore) {
        adviceGuy();
      }
    }
    
    // tarkista CO2-kulutus
    co2Consumption();
    // kartan merkit
    updateMapMarkers();
    
    if (!canTravelToAnyAvailableAirport()) {
      openPopup('defeat-modal', 'https://st2.depositphotos.com/1074442/7027/i/450/depositphotos_70278557-stock-photo-fallen-chess-king-as-a.jpg');
    }
  }
}

// testaa onko pelaajalla tarpeeksi rahaa matkustaa vähintään yhdelle lentokentälle
function canTravelToAnyAvailableAirport() {
  for (let airport of gameData.available_airports_info) {
    if (airport.flight_info.can_fly_to) {
      return true;
    }
  }
  return false;
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
  
  // lisää markerille popup
  marker.bindPopup(flightInfoMarkerPopup);
  
  // jos voi lentää, lisää lentonappi
  if (airportInfo.flight_info.can_fly_to) {
    // lentonappi
    const flyButton = document.createElement('button');
    flyButton.classList.add('button');
    flyButton.innerHTML = 'Fly';
    
    // mahdollistaa napin keskittämisen
    const flyButtonContainer = document.createElement('div');
    flyButtonContainer.append(flyButton);
    flightInfoMarkerPopup.append(flyButtonContainer);
  
    // event napille
    flyButton.addEventListener('click', async function() {
      const response = await fetch(flyToUrl + `/${gameId}/${airportInfo.icao}`);
      if (!response.ok) {
        throw new Error('Invalid server input!');
      }
      gameData = await response.json();
      updateStatus(airportInfo.visited);
    });
  }
}

// testaa CO2-kulutus
function co2Consumption() {
  if (gameData.game_info.co2_consumed >= 1000 && !co2AlertShown) {
    // avaa CO2-modal
    document.querySelector('#co2-modal').classList.remove('hide');
    co2AlertShown = true;

    // päivittää CO2-kulutuksen värin
    document.querySelector('#co2').style.color = 'red';
  }
}

// sulje co2-form
document.querySelector('#close-co2').addEventListener('click', function () {
  document.querySelector('#co2-modal').classList.add('hide');
})

// sulje story-form
document.querySelector('#close-story').addEventListener('click', function () {
  document.querySelector('#story-modal').classList.add('hide');
})

// sulje treasure-land-form
document.querySelector('#close-treasure-land').addEventListener('click', function () {
  document.querySelector('#treasure-land-modal').classList.add('hide');
})

// advice guy antaa neuvon
function adviceGuy() {
  // päivitä advice guy palkinto ja neuvo HTML:ään
  document.querySelector('#advice-guy-money').innerHTML = 'You encounter an advice guy!';
  document.querySelector('#advice-guy-money2').innerHTML = `You get ${gameData.game_info.advice_guy_reward} €.`;
  document.querySelector('#advice-guy-advice').innerHTML = `Advice: ${gameData.current_location_info.advice_guy.advice}`;
  openPopup('advice-guy-modal', 'https://cloudfront-us-east-1.images.arcpublishing.com/bostonglobe/MIBPKIJCBDUDEWE5TPCVMOKMNA.JPG');
}

// testaa onko wise man, johon ei ole vastattu
function hasUnansweredWiseMan() {
  if (gameData.current_location_info.wise_man && gameData.current_location_info.wise_man.answered === 0) {
  return true;
  } else {
    return false;
  }
}

// wise man kysyy haluaako pelaaja kuulla kysymyksen sekä kysyy kysymyksen
async function wiseManQuestion() {
  // päivitä wise man teksti (jos pelaaja löytää aarteen edellisessä pelissä, teksti on eri)
  document.querySelector('#final-wise-man-text').innerHTML = 'Wise man question:';

  // päivitä wise man hinta HTML:ään
  document.querySelector('#wise-man-cost').innerHTML = `Cost: ${gameData.game_info.wise_man_cost} €`;
  if (hasUnansweredWiseMan() && (await handleYesOrNoQuestion()) === 'yes') {
    // päivitä wise man hinta HTML:ään
    document.querySelector('#wise-man-cost').innerHTML = `Cost: ${gameData.game_info.wise_man_cost} €`;

    // päivitä kysymys HTML:ään
    document.querySelector('#wise-man-question').innerHTML = `${gameData.current_location_info.wise_man.wise_man_question}`;

    // kysy kysymys sekä odota vastausta
    const userAnswer = await handleWiseManQuestion();
    
    // 1 oikea vastaus, 0 väärä vastaus
    let isCorrectAnswer = userAnswer === gameData.current_location_info.wise_man.answer ? 1 : 0;
    
    // tulostukset riippuen oliko vastaus oikein vai väärin
    if (isCorrectAnswer === 1) {

      // päivitä voittoraha HTML:ään
      document.querySelector('#moneyAmount').innerHTML = `Correct answer! You won ${gameData.game_info.wise_man_reward} €.`;

      // avaa oikea vastaus popup
      await openPopup('right-answer-modal', 'https://media.tenor.com/1UgbfxIH5ywAAAAe/11.png');
      
    } else {
      await openPopup('wrong-answer-modal', 'https://i.redd.it/rcw85kdf7ls41.jpg');

      // päivitä häviöraha HTML:ään
      document.querySelector('#moneyAmount').innerHTML = 'Wrong answer!';
    }
    
    // lähettää tiedon vastauksen oikeellisuudesta palvelimelle, joka lisää tai poistaa rahaa
    const response = await fetch(wiseManUrl + `/${gameId}/` + isCorrectAnswer);
    if (!response.ok) {
      throw new Error('Invalid server input!');
    }
    // päivittynyt data
    gameData = await response.json();
    console.log(gameData);
  }
}

// final wise man aarteen luona, pakko vastata
async function finalWiseManQuestion() {
  if (hasUnansweredWiseMan()) {
    // päivitä kysymys
    document.querySelector('#wise-man-question2').innerHTML = `${gameData.current_location_info.wise_man.wise_man_question}`;

    // kysy kysymys
    const userAnswer = await handleLastWiseManQuestion();

    // 1 oikea vastaus, 0 väärä vastaus
    let isCorrectAnswer = userAnswer === gameData.current_location_info.wise_man.answer ? 1 : 0;

    // tulostukset riippuen oliko vastaus oikein vai väärin
    if (isCorrectAnswer === 1) {

      // avaa voitto pop up
      await openPopup('victory-modal', 'https://images.freeimages.com/images/large-previews/863/chest-1558928.jpg?fmt=webp&w=500'); /*'https://www.commandpostgames.com/wp-content/uploads/2017/03/victory.jpg');*/

    } else {
      openPopup('defeat-modal2', 'https://st2.depositphotos.com/1074442/7027/i/450/depositphotos_70278557-stock-photo-fallen-chess-king-as-a.jpg');

    }
  }
}

// aloita peli
document.querySelector('#start').addEventListener('click', startNewGame);

// aarrearkun avaus
document.querySelector('#treasure').addEventListener('click', function () {

  // lisää aarre formille
  document.querySelector('#treasure-text').innerHTML = `The treasure is <b>${gameData.current_location_info.treasure}</b>!
  Congratulations!`;

  // avaa aarre-form
  document.querySelector('#opened-chest-modal').classList.remove('hide');
})

// sulje form close-napista
document.querySelector('.close-button').addEventListener('click', function (evt) {
  evt.preventDefault();
  document.getElementById('opened-chest-modal').classList.add('hide');
})

// popupit

function openPopup(popupId, imageUrl) {
  return new Promise((resolve) => {
    var popup = document.getElementById(popupId);
    var imgElement = popup.querySelector('.popup-content img')

    if (imgElement && imageUrl) {
      imgElement.src = imageUrl;
    }

    popup.classList.remove('hide');
    popup.style.display = 'block';

    var yesButton = popup.querySelector('#yes');
    var noButton = popup.querySelector('#no');
    var option1Button = popup.querySelector('#option1');
    var option2Button = popup.querySelector('#option2');
    var option3Button = popup.querySelector('#option3');
    var optionAButton = popup.querySelector('#optionA');
    var optionBButton = popup.querySelector('#optionB');
    var optionCButton = popup.querySelector('#optionC');
    var closeButton = popup.querySelector('.close');
    var treasureButton = popup.querySelector('#treasure');

    if (yesButton) {
      yesButton.addEventListener('click', function() {
        resolve('yes');
        closePopup(popupId);
      });
    }

    if (noButton) {
      noButton.addEventListener('click', function() {
        resolve('no');
        closePopup(popupId);
      });
    }

    if (option1Button) {
      option1Button.addEventListener('click', function() {
        resolve('a');
        closePopup(popupId);
      });
    }

    if (option2Button) {
      option2Button.addEventListener('click', function() {
        resolve('b');
        closePopup(popupId);
      });
    }

    if (option3Button) {
      option3Button.addEventListener('click', function() {
        resolve('c');
        closePopup(popupId);
      });
    }

    if (optionAButton) {
      optionAButton.addEventListener('click', function() {
        resolve('a');
        closePopup(popupId);
      });
    }

    if (optionBButton) {
      optionBButton.addEventListener('click', function() {
        resolve('b');
        closePopup(popupId);
      });
    }

    if (optionCButton) {
      optionCButton.addEventListener('click', function() {
        resolve('c');
        closePopup(popupId);
      });
    }

    if (closeButton) {
      closeButton.addEventListener('click', function() {
        resolve(null);
        closePopup(popupId);
      });
    }

    if (treasureButton) {
      treasureButton.addEventListener('click', function() {
        resolve('treasure');
        closePopup(popupId);
      });
    }
  });
}

function closePopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.classList.add('hide');
  popup.style.display = 'none';
}

var closeButtons = document.getElementsByClassName('close');

for (var i = 0; i < closeButtons.length; i++) {
  closeButtons[i].addEventListener('click', function() {
    var popupId = this.getAttribute('data-popup');
    closePopup(popupId);
  });
}

async function handleWiseManQuestion() {
  return await openPopup('wise-man-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
}

async function handleLastWiseManQuestion() {
  return await openPopup('final-wise-man-modal', 'https://cdn.pixabay.com/photo/2019/08/07/18/00/lotr-4391263_1280.png');
}

async function handleYesOrNoQuestion() {
  return await openPopup('yes-or-no-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
}
