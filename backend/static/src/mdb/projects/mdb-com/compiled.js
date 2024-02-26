// CUSTOM JS
import './js/clipboard.js';
import './js/new-prism.js';
import './js/for-thieves.js';

// MDB JS
import * as mdbPro from '../../js/mdb.pro.umd.js';
const { initMDB } = mdbPro;

const compiled = { ...mdbPro };
initMDB(compiled);

export default compiled;
