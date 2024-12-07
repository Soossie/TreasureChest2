'use strict';

// scrollaa loppuun

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
let stillPlaying = true;
let co2AlertShown = false;

// aloita uusi peli
async function startNewGame() {
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
  updateStatus(gameData, NaN);
}

// päivitä pelaajan tiedot
function updatePlayerInfoPanel(data) {
  document.querySelector('#player').innerHTML = `${data.game_info.screen_name}`;
  document.querySelector('#money').innerHTML = `${data.game_info.money}`;
  document.querySelector('#location').innerHTML = `${data.current_location_info.name}`;
  document.querySelector('#co2').innerHTML = `${data.game_info.co2_consumed}`;
  document.querySelector('#clue').innerHTML = `${data.game_info.clue}`;
}

// päivitä nykyinen sijainti kartalle
function updateCurrentLocationMarkerOnly(data) {
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
}

// päivitä nykyinen sijainti ja kaikki lentokentät kartalle
function updateMapMarkers(data) {
  // nykyinen sijainti
  updateCurrentLocationMarkerOnly(data);

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

// ohjelma odottaa x ms. odotuksen aikana nykyinen sijainti ehtii päivittyä kartalle,
// jolloin esim. mahdollisen tietäjän sattuessa kohdalle pelaajan kartta on keskittynyt uudelle sijainnille
function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

// päivittää pelin tiedot käyttöliittymään
async function updateStatus(data, visitedBefore=false) {
  console.log(data);
  
  updatePlayerInfoPanel(data);
  
  // odota x millisekuntia jotta nykyinen sijainti päivittyy kartalle
  updateCurrentLocationMarkerOnly(data);
  await delay(200);
  
  // tarkista onko kentällä aarre
  if (data.current_location_info.has_treasure) {
    stillPlaying = false;
    openPopup('victory-modal', 'https://www.commandpostgames.com/wp-content/uploads/2017/03/victory.jpg');
    //alert(`You won!`);  // tähän pop up, kerro aarre
    
  } else {
    if (data.current_location_info.wise_man) {  // wise man
      // testaa onko wise man, jos on niin kyselyt
      wiseManQuestion(data);
      updatePlayerInfoPanel(data);
      
    } else if (data.current_location_info.advice_guy) {  // advice guy
      // testaa onko kentällä käyty, jos ei ole kerro vinkki
      if (visitedBefore === false) {
        adviceGuy(data);
      }
    }
    
    // tarkista CO2-kulutus
    co2Consumption(data);
    
    // kartan merkit
    updateMapMarkers(data);
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
    
    updateStatus(data, airportInfo.visited);

    // päivitä game status tiedot uudelleen? wise man rahat ei päivity ui, mutta dataan kyllä. wise man raha
    //   päivittyy vasta seuraavan lennon yhteydessä

  });
}

// testaa onko aarretta (aarremaassa)
function treasure(data) {
  if (data.game_info.in_treasure_land && data.current_location_info.has_treasure === 1) {
    openPopup('victory-modal', 'https://www.commandpostgames.com/wp-content/uploads/2017/03/victory.jpg');
    // pitäisi estää lentäminen voittoviestin jälkeen
  } else {
    console.log('Treasure not found.');
  }
}

// testaa CO2-kulutus, jos yli 1000 kg niin tulee alert ja teksti muuttuu punaiseksi
function co2Consumption(data) {
  if (data.game_info.co2_consumed >= 1000 && !co2AlertShown) {
    alert('You have consumed over 1000 kg CO2! You have to pay CO2 emission-based flight tax for each flight.');
    co2AlertShown = true;
    // lentolippujen hinta on kalliimpi, miten päivittyy?
    // päivittää CO2-kulutuksen värin
    document.querySelector('#co2').style.color = 'red';
  }
}


// advice guy funktiot

// testaa onko advice guy
function hasAdviceGuy(data) {
  if (data.current_location_info.advice_guy) {
    console.log('Advice guy found!');
    return true;
  } else {
    console.log('No advice guy here.')
    return false;
  }
}

// advice guy antaa neuvon (rahamäärä päivittyy jo pythonissa)
function adviceGuy(data) {
  if (hasAdviceGuy(data)) {

    // päivitä advice guy palkinto ja neuvo HTML:ään
    document.querySelector('#advice-guy-money').innerHTML = 'You encounter an advice guy!';
    document.querySelector('#advice-guy-money2').innerHTML = `You get ${data.game_info.advice_guy_reward} €.`;
    document.querySelector('#advice-guy-advice').innerHTML = `Advice: ${data.current_location_info.advice_guy.advice}`;

    openPopup('advice-guy-modal', 'https://cloudfront-us-east-1.images.arcpublishing.com/bostonglobe/MIBPKIJCBDUDEWE5TPCVMOKMNA.JPG');
  }
}




// wise man funktioiden alku

// testaa onko wise man, johon ei ole vastattu
function hasUnansweredWiseMan(data) {
  if (data.current_location_info.wise_man && data.current_location_info.wise_man.answered === 0) {
  console.log("Unanswered wise man found!");
  return true;
  } else {
    console.log("No wise man data found.");
    return false;
  }
}

// wise man kysyy haluaako pelaaja kuulla kysymyksen sekä kysyy kysymyksen
async function wiseManQuestion(data) {

  if (hasUnansweredWiseMan(data) && (await handleYesOrNoQuestion()) === 'yes') {
    // päivitä wise man hinta HTML:ään
    document.querySelector('#wise-man-cost').innerHTML = `Cost: ${data.game_info.wise_man_cost} €.`;

    // päivitä kysymys HTML:ään
    document.querySelector('#wise-man-question').innerHTML = `Question: ${data.current_location_info.wise_man.wise_man_question}`;

    // kysy kysymys sekä odota vastausta
    const userAnswer = await handleWiseManQuestion();

    if (userAnswer === data.current_location_info.wise_man.answer) {
      console.log('Correct!')

      // päivitä voittoraha HTML:ään
      document.querySelector('#moneyAmount').innerHTML = `Correct answer! You won ${data.game_info.wise_man_reward} €.`;

      // avaa oikea vastaus popup
      await openPopup('right-answer-modal', 'https://media.tenor.com/1UgbfxIH5ywAAAAe/11.png');

      // päivittää rahan, kun vastaus oikein
      const response = await fetch(wiseManUrl + `/${gameId}/` + 1);
      if (!response.ok) {
        throw new Error('Invalid server input!');
      }
    } else {
      console.log('Wrong answer.');
      await openPopup('wrong-answer-modal', 'https://i.redd.it/rcw85kdf7ls41.jpg');

      // päivitä häviöraha HTML:ään
      document.querySelector('#moneyAmount').innerHTML = 'Wrong answer!';
      // päivittää rahan, kun vastaus väärin
      const response = await fetch(wiseManUrl + `/${gameId}/` + 0);
      if (!response.ok) {
        throw new Error('Invalid server input!');
      }
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
    var closeButton = popup.querySelector('.close');

    if (yesButton) {
      yesButton.onclick = function() {
        resolve('yes');
        closePopup(popupId);
      };
    }

    if (noButton) {
      noButton.onclick = function() {
        resolve('no');
        closePopup(popupId);
      };
    }

    if (option1Button) {
      option1Button.onclick = function() {
        resolve('a');
        closePopup(popupId);
      };
    }

    if (option2Button) {
      option2Button.onclick = function() {
        resolve('b');
        closePopup(popupId);
      };
    }

    if (option3Button) {
      option3Button.onclick = function() {
        resolve('c');
        closePopup(popupId);
      };
    }

    if (closeButton) {
      closeButton.onclick = function() {
        resolve(null);
        closePopup(popupId);
      };
    }
  });
}

function closePopup(popupId) {
  var popup = document.getElementById(popupId);
  popup.classList.add('hide');
  popup.style.display = 'none';
}

var btn1 = document.getElementById('open-wise-man-modal-popup');
var btn2 = document.getElementById('open-advice-guy-modal-popup');
var btn3 = document.getElementById('open-victory-modal-popup');
var btn4 = document.getElementById('open-defeat-modal-popup');
var btn5 = document.getElementById('open-yes-or-no-popup');
var btn6 = document.getElementById('open-right-answer-popup');
var btn7 = document.getElementById('open-wrong-answer-popup');

var closeButtons = document.getElementsByClassName('close');

btn1.onclick = function() {
  openPopup('wise-man-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
};

btn2.onclick = function() {
  openPopup('advice-guy-modal', 'https://cloudfront-us-east-1.images.arcpublishing.com/bostonglobe/MIBPKIJCBDUDEWE5TPCVMOKMNA.JPG');
};

btn3.onclick = function() {
  openPopup('victory-modal', 'https://www.commandpostgames.com/wp-content/uploads/2017/03/victory.jpg');
};

btn4.onclick = function() {
  openPopup('defeat-modal', 'https://st2.depositphotos.com/1074442/7027/i/450/depositphotos_70278557-stock-photo-fallen-chess-king-as-a.jpg');
};

btn5.onclick = function() {
  openPopup('yes-or-no-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
};

btn6.onclick = function() {
  openPopup('right-answer-modal', 'https://media.tenor.com/1UgbfxIH5ywAAAAe/11.png');
}

btn7.onclick = function() {
  openPopup('wrong-answer-modal', 'https://i.redd.it/rcw85kdf7ls41.jpg');
}

for (var i = 0; i < closeButtons.length; i++) {
  closeButtons[i].onclick = function() {
    var popupId = this.getAttribute('data-popup');
    closePopup(popupId);
  };
}

async function handleWiseManQuestion() {
  const result = await openPopup('wise-man-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
  console.log('user answer:', result);
  return result;
}

async function handleYesOrNoQuestion() {
  const result = await openPopup('yes-or-no-modal', 'https://miro.medium.com/v2/resize:fit:1024/1*CBHr0zEVsCe_sWubk6mviw.jpeg');
  console.log('user answer:', result);
  return result;
}