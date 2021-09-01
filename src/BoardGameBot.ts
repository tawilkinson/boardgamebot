/* eslint-disable @typescript-eslint/no-var-requires */

require('dotenv').config();
require('module-alias/register');

import { BGClient } from '@lib/BGClient';

const bgbot = new BGClient();

void bgbot.login(bgbot.production ? process.env.DISCORD_TOKEN_PROD : process.env.DISCORD_TOKEN_DEV);