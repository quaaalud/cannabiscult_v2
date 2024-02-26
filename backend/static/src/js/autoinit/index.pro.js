import defaultInitSelectors from './initSelectors/pro.js';
import { InitMDB } from './init.js';
import { Datatable } from '../pro/datatable/index.js';

const initMDBInstance = new InitMDB(defaultInitSelectors);
const initMDB = initMDBInstance.initMDB;

export default initMDB;
