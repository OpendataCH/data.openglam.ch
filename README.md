# Swiss Open GLAM Data

## Hints for adding new datasets

- Add yml file inside _datasets
- Use subfolder with institution name in English
- The url is defined by the yml file name
- 


## Software behind the tool : JKAN

The software used for display is called [JKAN](https://jkan.io), A lightweight, backend-free open data portal, powered by Jekyll.

[Demo site](https://demo.jkan.io)


### Build locally

```shell
docker compose up
```
And open it on http://127.0.0.1:4000


Update bundled javascript (which is in scripts/dist folder) after a change in javascript files
```shell
npm run build
```

### Documentation
* [Installation](docs/installation.md)
* [Upgrading](docs/upgrading.md)
* [Schema customization](docs/schema-customization.md)
* [Running locally](docs/running-locally.md)
* [Architecture](docs/architecture.md)
