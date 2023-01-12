import httpx
import pytest
import respx

from erclient import (ERClientException, ERClientNotFound,
                      ERClientPermissionDenied, ERClientServiceUnavailable)


@pytest.mark.asyncio
async def test_post_sensor_observation_success(er_client, position, position_created_response):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a successful response
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(
            httpx.codes.CREATED, json=position_created_response)
        # Send a position using the async client
        response = await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        assert response == {}
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_connect_timeout(er_client, position):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a connection timeout error
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.side_effect = httpx.ConnectTimeout
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientException):
            await er_client.post_sensor_observation(position)
            assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_response_timeout(er_client, position):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a read timeout error
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.side_effect = httpx.ReadTimeout
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientException):
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_status_gateway_timeout(er_client, position):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a gateway timeout
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(
            httpx.codes.GATEWAY_TIMEOUT, json={})
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientServiceUnavailable, match='ER service unavailable'):
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_status_bad_gateway(er_client, position):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a bad gateway error
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(httpx.codes.BAD_GATEWAY, json={})
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientServiceUnavailable, match='ER service unavailable'):
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_status_bad_request(er_client, position, bad_request_response):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a client error
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(
            httpx.codes.BAD_REQUEST, json=bad_request_response)
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientException) as e:
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_status_forbidden(er_client, position, forbidden_response):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a permissions error
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(
            httpx.codes.FORBIDDEN, json=forbidden_response)
        # Check that the right exception is raised by the client
        expected_reason = forbidden_response['status']['detail']
        with pytest.raises(ERClientPermissionDenied, match=expected_reason):
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()


@pytest.mark.asyncio
async def test_post_sensor_observation_status_not_found(er_client, position, not_found_response):
    async with respx.mock(
            base_url=er_client.service_root, assert_all_called=False
    ) as respx_mock:
        # Mock the call to the ER API and simulate a not found response
        route = respx_mock.post(
            f'/sensors/generic/{er_client.provider_key}/status')
        route.return_value = httpx.Response(
            httpx.codes.NOT_FOUND, json=not_found_response)
        # Check that the right exception is raised by the client
        with pytest.raises(ERClientNotFound):
            await er_client.post_sensor_observation(position)
        assert route.called  # Check that the api endpoint was called
        await er_client.close()
