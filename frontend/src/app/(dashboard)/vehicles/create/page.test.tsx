import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CreateVehiclePage from './page';

const pushMock = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock }),
}));

const createVehicleMock = jest.fn();
jest.mock('@/hooks/useVehicleTracking', () => ({
  useVehicleTracking: () => ({ createVehicle: createVehicleMock }),
}));

function fillRequiredFields() {
  fireEvent.change(screen.getByLabelText(/Vehicle Name/i), { target: { value: 'Delivery Van 1' } });
  fireEvent.change(screen.getByLabelText(/Plate Number/i), { target: { value: 'AA-1234' } });
}

describe('CreateVehiclePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('strips empty optional fields from the payload before submitting', async () => {
    createVehicleMock.mockResolvedValue({ id: 'v-1' });
    render(<CreateVehiclePage />);

    fillRequiredFields();
    // make, model, year, device_id, color are all left blank.
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    await waitFor(() => expect(createVehicleMock).toHaveBeenCalled());
    const payload = createVehicleMock.mock.calls[0][0];

    expect(payload).toEqual({ name: 'Delivery Van 1', plate_number: 'AA-1234', type: 'car' });
    expect(payload).not.toHaveProperty('make');
    expect(payload).not.toHaveProperty('model');
    expect(payload).not.toHaveProperty('year');
    expect(payload).not.toHaveProperty('device_id');
    expect(payload).not.toHaveProperty('color');
  });

  it('keeps optional fields that were actually filled in, including numeric year', async () => {
    createVehicleMock.mockResolvedValue({ id: 'v-2' });
    render(<CreateVehiclePage />);

    fillRequiredFields();
    fireEvent.change(screen.getByLabelText(/Make/i), { target: { value: 'Toyota' } });
    fireEvent.change(screen.getByLabelText(/Year/i), { target: { value: '2023' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    await waitFor(() => expect(createVehicleMock).toHaveBeenCalled());
    const payload = createVehicleMock.mock.calls[0][0];

    expect(payload.make).toBe('Toyota');
    expect(payload.year).toBe(2023);
  });

  it('redirects to the vehicle list on success', async () => {
    createVehicleMock.mockResolvedValue({ id: 'v-3' });
    render(<CreateVehiclePage />);

    fillRequiredFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/vehicles'));
  });

  it('surfaces a string error message returned by the API', async () => {
    createVehicleMock.mockRejectedValue({ response: { data: { detail: 'Plate number already in use' } } });
    render(<CreateVehiclePage />);

    fillRequiredFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    expect(await screen.findByText('Plate number already in use')).toBeInTheDocument();
    expect(pushMock).not.toHaveBeenCalled();
  });

  it('joins a validation-array error response into one message', async () => {
    createVehicleMock.mockRejectedValue({
      response: { data: { detail: [{ msg: 'plate_number required' }, { msg: 'invalid type' }] } },
    });
    render(<CreateVehiclePage />);

    fillRequiredFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    expect(await screen.findByText('plate_number required, invalid type')).toBeInTheDocument();
  });

  it('falls back to a generic message when the API gives no detail', async () => {
    createVehicleMock.mockRejectedValue({});
    render(<CreateVehiclePage />);

    fillRequiredFields();
    fireEvent.click(screen.getByRole('button', { name: /Create Vehicle/i }));

    expect(await screen.findByText('Failed to create vehicle')).toBeInTheDocument();
  });
});
