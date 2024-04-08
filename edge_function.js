const api = require('./api');

module.exports = async (req, res) => {
    if (req.method === 'GET' && req.url === '/') {
        // Logic for handling GET request to '/'
        const a = ['Population Growth since 2000', 'Poverty Rate', 'College Graduates', 'Crime Index', 'Median Household Income', 'Median Household Income Growth since 2000', 'Landlord Friendly', 'Median Household Value', 'Median Household Value Growth since 2000', 'Owner Occupied Housing Unit Rate', 'Median Gross Rent', 'Median Gross Rent vs. Median HH Income', 'Max Possible Rent', 'Liveability Score', 'Vacancy Rate', 'Job Growth', 'Unemployment Rate'];
        const ekpi = {
            KPI: a,
            Value: Array(17).fill(''),
            Comment: Array(17).fill('')
        };
        const c = ['Studio', '1-BD', '2-BD', '3-BD', '4-BD'];
        const erent = {
            Type: c,
            min: Array(5).fill(''),
            max: Array(5).fill('')
        };
        res.status(200).send({
            result: false,
            ekpi: ekpi,
            erent: erent
        });
    } else if (req.method === 'POST' && req.url === '/submit') {
        // Logic for handling POST request to '/submit'
        const { Email, Name, phoneNumber, zipcode } = req.body;
        const capture_data = api.capture_data;
        const get_zip_data = api.get_zip_data;
        const get_rent = api.get_rent;
        const jd = api.jd;
        const get_data = api.get_data;

        const user_data = [Email, Name, phoneNumber, zipcode];
        capture_data(user_data);
        const info = get_zip_data(zipcode);

        if (zipcode && info) {
            const rents = get_rent(info);
            const jds = jd(info);
            const KPIs = get_data(zipcode, info, rents);

            res.status(200).send({
                result: true,
                zipcode: zipcode,
                KPIs: KPIs,
                rents: rents,
                jd: jds,
                Email: Email,
                Name: Name,
                phoneNumber: phoneNumber
            });
        } else {
            res.status(400).send("Please enter a valid zip code!");
        }
    } else {
        // Handle other routes or methods (e.g., 404 Not Found)
        res.status(404).send('Not Found');
    }
};
