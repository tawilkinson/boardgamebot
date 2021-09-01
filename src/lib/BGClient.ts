import './setup';
import { SapphireClient} from '@sapphire/framework';
import { CLIENT_OPTIONS } from '../config';

export class BGClient extends SapphireClient{
	public production: boolean;
	
	public constructor() {
		super(CLIENT_OPTIONS);
		this.production = process.env.NODE_ENV === "development";
	};
	
}
