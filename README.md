# Stewart Filmscreen CVM Integration for Home Assistant

This custom integration for Home Assistant allows users to control Stewart Filmscreen CVM motorized screens directly from their Home Assistant instance. By integrating these screens into Home Assistant, users can create a more cohesive and automated smart home environment. This integration adds a cover entity for each motor, enabling control over the position of your Stewart Filmscreen systems. Additionally, it provides the services `recall_preset` and `store_preset` to save and recall motor positions, making it easier to manage different viewing preferences.

## Features

- Control Stewart Filmscreen CVM motors as cover entities in Home Assistant.
- Save motor positions with `store_preset` service.
- Recall saved motor positions with `recall_preset` service.

## Prerequisites

- Home Assistant instance (at minimum 2024.1.5).
- HACS (Home Assistant Community Store) installed on your Home Assistant.
- Stewart Filmscreen CVM system set up and accessible within the same network as your Home Assistant.

## Installation

### Via HACS

1. Open HACS in your Home Assistant interface.
2. Go to "Integrations" and click on the "+ Explore & Download Repositories" button in the bottom right corner.
3. Search for "Stewart Filmscreen CVM" and select it.
4. Click on "Download this Repository" and select the version you wish to install.
5. Restart Home Assistant to apply the changes.

### Manual Installation

1. Download the latest release from the GitHub repository.
2. Unzip the release and copy the `custom_components/stewart_filmscreen_cvm` folder to your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant to apply the changes.

## Configuration

After installation, add the Stewart Filmscreen CVM integration via the Home Assistant UI:

1. Navigate to Configuration > Integrations.
2. Click on the "+ Add Integration" button.
3. Search for "Stewart Filmscreen CVM" and select it.
4. Follow the on-screen instructions to complete the setup.

## Usage

### Controlling Motors

Use the cover entity controls within Home Assistant to open, close, or set the position of your Stewart Filmscreen CVM motors.

### Saving and Recalling Presets

- To save a motor position, call the `store_preset` service with the motor entity and desired preset name.
- To recall a saved position, call the `recall_preset` service with the motor entity and the preset name.

## Documentation

For more detailed information on the Stewart Filmscreen CVM and its capabilities, please refer to the official documentation: [Stewart Filmscreen CVM Documentation](https://www.stewartfilmscreen.com/Files/files/Support%20Material/Controls/CVM.pdf).

## Support

If you encounter any issues or have questions about this integration, please open an issue on the GitHub repository.

## Contributing

Contributions to improve the integration are welcome. Please refer to the repository's contribution guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Stewart Filmscreen for providing the documentation needed to develop this integration.
- This integration is not officially affiliated with or endorsed by Stewart Filmscreen.