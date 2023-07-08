public async Task<IList<CarParkProductDto>> GetProductsAsync(CarParkProductSearchRequestDto carParkSearchRequest, CancellationToken cancellationToken)
{
    var availabilityRequest = new ProductAvailableRequest
    {
        EffectiveFrom = carParkSearchRequest.EntryFrom,
        EffectiveTo= carParkSearchRequest.ExitBy,
        PromoCode = carParkSearchRequest.PromoCode
    };
    _logger.LogInformation("Initiating car parking request for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);

    var result = await _ubiParkDataAccessService.AvailableCarParkProductsList(availabilityRequest, cancellationToken);
    if (!result.Success || result.Products == null)
    {
        _logger.LogWarning("Car parking request did not return availability for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);
        return new List<CarParkProductDto>();
    }
    var carProducts = result.Products.Where(p => p.Result).Select(cp => _mapper.Map<CarParkProductDto>(cp)).ToList();
    //re-populate promoCode value as currently response does not return sent in request promo code
    carProducts.ForEach(p => p.PromoCode = carParkSearchRequest.PromoCode!);
    return carProducts.ToList();
}