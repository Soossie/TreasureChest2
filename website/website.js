'use strict';

// scrollaa loppuun

const map = L.map('map', { tap: false });
L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
}).addTo(map);
//map.setView([60, 24], 7);

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
const newGameUrl = apiUrl + '/new-game'
const gameInfoUrl = apiUrl + '/game-info'

let gameId;

// aloita uusi peli
async function startNewGame() {
  // muuta prompt formiksi
  const playerName = prompt('Input name: ')
  const difficultyLevel = prompt('Input difficulty level (e / n / h): ')
  
  const response = await fetch(newGameUrl + `/${playerName}` + `/${difficultyLevel}`);
  if (!response.ok) throw new Error('Invalid server input!');
  return await response.json();
}

async function gameSetup(){
  const gameData = await startNewGame();
  console.log(gameData);
  updateStatus(gameData);
  gameId = gameData.game_info.id;
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
  
  // karttamerkit
  let marker = L.marker([data.current_location_info.latitude, data.current_location_info.longitude]).addTo(map);
  map.setView([data.current_location_info.latitude, data.current_location_info.longitude], 4);
  // lisää kaikki lentokentät tähän. löytyy datasta kohdasta available_airports_info. muuta eri värisiksi
  
}


// valitse näistä yksi:

// tekee uuden pelin
//gameSetup(apiUrl);

// voit käyttä testaukseen guiSetup, ei tee uutta peliä
guiSetup();


