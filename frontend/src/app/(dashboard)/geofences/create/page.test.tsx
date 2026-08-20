import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CreateGeofencePage from './page';

const pushMock = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const createGeofenceMock = jest.fn();
jest.mock('@/hooks/useGeofence', () => ({
  useGeofence: () => ({ createGeofence: createGeofenceMock }),
}));

jest.mock('@/components/map/LiveMap', () => ({
  __esModule: true,
  default: () => <div data-testid="live-map-stub" />,
}));

function fillCircleFields() {
  fireEvent.change(screen.getByLabelText(/Geofence Name/i), { target: { value: 'Depot' } });
  fireEvent.change(screen.getByLabelText(/Center Latitude/i), { target: { value: '9.01' } });
  fireEvent.change(screen.getByLabelText(/Center Longitude/i), { target: { value: '38.75' } });
  fireEvent.change(screen.getByLabelText(/Radius/i), { target: { value: '500' } });
}

describe('CreateGeofencePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('blocks submission and shows an error when circle fields are missing', async () => {
    render(<CreateGeofencePage />);

    fireEvent.change(screen.getByLabelText(/Geofence Name/i), { target: { value: 'Depot' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Geofence/i }));

    expect(
      await screen.findByText('Center latitude, longitude and radius are required for circle geofences.')
    ).toBeInTheDocument();
    expect(createGeofenceMock).not.toHaveBeenCalled();
  });

  it('submits a valid circle geofence with numeric fields and redirects to the list', async () => {
    createGeofenceMock.mockResolvedValue({ id: 'g-1' });
    render(<CreateGeofencePage />);

    fillCircleFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Geofence/i }));

    await waitFor(() =>
      expect(createGeofenceMock).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Depot',
          type: 'circle',
          center_lat: 9.01,
          center_lng: 38.75,
          radius_meters: 500,
        })
      )
    );
    expect(pushMock).toHaveBeenCalledWith('/geofences');
  });

  it('surfaces a string error message returned by the API', async () => {
    createGeofenceMock.mockRejectedValue({ response: { data: { detail: 'Name already exists' } } });
    render(<CreateGeofencePage />);

    fillCircleFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Geofence/i }));

    expect(await screen.findByText('Name already exists')).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it('joins a validation-array error response into one message', async () => {
    createGeofenceMock.mockRejectedValue({
      response: { data: { detail: [{ msg: 'field required' }, { msg: 'invalid color' }] } },
    });
    render(<CreateGeofencePage />);

    fillCircleFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Geofence/i }));

    expect(await screen.findByText('field required, invalid color')).toBeInTheDocument();
  });

  it('falls back to a generic message when the API gives no detail', async () => {
    createGeofenceMock.mockRejectedValue({});
    render(<CreateGeofencePage />);

    fillCircleFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Geofence/i }));

    expect(await screen.findByText('Failed to create geofence')).toBeInTheDocument();
  });

  it('disables the submit button and hides circle fields for polygon type', () => {
    render(<CreateGeofencePage />);

    fireEvent.click(screen.getByRole('button', { name: /Polygon/i }));

    expect(screen.getByRole('button', { name: /Create Geofence/i })).toBeDisabled();
    expect(screen.queryByLabelText(/Center Latitude/i)).not.toBeInTheDocument();
  });
});
